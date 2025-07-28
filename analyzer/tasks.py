from celery import shared_task
from tensorflow.keras.applications import mobilenet_v2, resnet50, efficientnet
from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from tensorflow.keras.preprocessing import image
import numpy as np
from io import BytesIO

from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction
from django.core.files.images import ImageFile
from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage
import boto3, os, uuid, requests, traceback

from .models import MstImages,TransAnalysis
from .category_map import CATEGORY_MAP  # カテゴリーマップのインポート
from .ai import load_effb0_custom, decode_1001, load_5class_model, decode_5class

MODEL_MAP = {
    'efficientnet_b0': (EfficientNetB0, efficientnet.preprocess_input, efficientnet.decode_predictions),
    'mobilenet_v2': (MobileNetV2, mobilenet_v2.preprocess_input, mobilenet_v2.decode_predictions),
    'resnet50': (ResNet50, resnet50.preprocess_input, resnet50.decode_predictions),
    'effb0_1001human': (load_effb0_custom, efficientnet.preprocess_input, decode_1001),
    'effb0_5class': (load_5class_model, efficientnet.preprocess_input, decode_5class),
}

def run_model_inference(model_name, image_data, use_category=True, top=30):
    ModelClass, preprocess, decode = MODEL_MAP.get(model_name, MODEL_MAP['efficientnet_b0'])
    model = ModelClass(weights='imagenet')
    x = preprocess(image_data)
    preds = model.predict(x)
    decoded = decode(preds, top=top)[0]

    best_label = decoded[0][1]
    best_score = decoded[0][2]

    from keras import backend as K
    K.clear_session()

    category_ranking = [] 
    if use_category:
        scores = {cat: 0.0 for cat in CATEGORY_MAP}
        for _, label, score in decoded:
            label_lower = label.lower()
            for category, keywords in CATEGORY_MAP.items():
                if label_lower in keywords:
                    scores[category] += score

        category_ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_label = category_ranking[0][0]
        best_score = category_ranking[0][1]


    return decoded, best_label, best_score, category_ranking


@shared_task
def analyze_image_task(analysis_id, full_path, model_name, use_category=True):
    try:
        analysis = None
        analysis = TransAnalysis.objects.get(pk=analysis_id)
        analysis.status = "解析中"
        analysis.started_at = timezone.now()
        analysis.use_category = use_category
        analysis.save()

        # 画像読み込み
        response = requests.get(full_path)
        response.raise_for_status()
        img = image.load_img(BytesIO(response.content), target_size=(224, 224))
        x = np.expand_dims(image.img_to_array(img), axis=0)

        # 推論
        decoded, best_label, best_score, category_ranking = run_model_inference(model_name, x, use_category, top=30)

        # decodeにカテゴリ集計結果を追加
        for rank, (cat, score) in enumerate(category_ranking, 1):
            decoded.append((
                None,
                f"{rank} {cat}",
                float(score)
            ))


        # Humanカテゴリなら専用推論
        if best_label == "Human (category)":
            _, _, human_score, _ = run_model_inference("effb0_1001human", x, use_category=True, top=10)
            # Human専用推論結果を追加（ラベル名を明示的に変更）
            decoded.append((
                None,
                "Human (specialized)",
                float(human_score)
            ))

            # best_score更新（高い方を採用）
            if human_score > best_score:
                best_score = human_score

        # DB登録（Human専用推論も含めてまとめて1回）
        analysis.top_preds = [
            {'label': lbl, 'prob': float(prob)}
            for (_id, lbl, prob) in decoded
        ]

        # 最終best_label / best_scoreを登録
        analysis.label = best_label
        analysis.reliability = best_score * 100
        analysis.status = "成功"

    except Exception as e:
        if analysis:
            analysis.status = "失敗"
            analysis.error_name = type(e).__name__
            analysis.error_log = traceback.format_exc()
            analysis.save()
        else: # DBエラーなどでanalysisが未定義の場合
            print("TransAnalysisレコード取得失敗:", e)

    finally:
        analysis.ended_at = timezone.now()
        analysis.save()
        import gc
        gc.collect()

@shared_task
def save_image_and_analyze_task(temp_path, user_id, model_name, use_category):
    s3_storage = S3Boto3Storage()
    s3_client = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)

    base, ext = os.path.splitext(os.path.basename(temp_path))
    safe = slugify(base)[:40] or "image"
    unique = uuid.uuid4().hex[:6]
    filename = f"{safe}-{unique}{ext.lower()}"
    with open(temp_path, "rb") as f:
        key = s3_storage.save(f"uploads/{filename}", ImageFile(f))

    os.remove(temp_path) # S3に保存後、一時ファイルを削除

    with transaction.atomic():
        mst_img = MstImages.objects.create(user_id=user_id, image=key)
        analysis = TransAnalysis.objects.create(
            image=mst_img,
            model_name=model_name,
            status="準備中"
        )

        signed_url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
            ExpiresIn=60 * 60 * 24
        )

    analyze_image_task.delay(
        analysis.analysis_id,
        signed_url,
        model_name,
        use_category
    )