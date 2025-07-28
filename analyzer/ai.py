import os
import json
import boto3
from tensorflow.keras.models import load_model
from django.conf import settings

# S3からダウンロード
def download_from_s3(bucket, key, local_path):
    """S3からダウンロード、既に存在するならスキップ"""
    if not os.path.exists(local_path):
        s3 = boto3.client('s3')
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            s3.download_fileobj(bucket, key, f)
        print(f"Downloaded {key} to {local_path}")
    else:
        print(f"Found local file: {local_path}")

# 起動時DL（1回だけ）
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
model_files = [
    ("models/effb0_1001human_model.keras", "models/effb0_1001human_model.keras"),
    ("models/effb0_5class_model.keras", "models/effb0_5class_model.keras"),
    ("models/imagenet_class_index_extended.json", "models/imagenet_class_index_extended.json"),
    ("models/class_index_5class.json", "models/class_index_5class.json"),
]
for s3_key, local_path in model_files:
    download_from_s3(BUCKET_NAME, s3_key, local_path)

# --- ImageNet 1001クラス用のラベルマップと関数 ---
with open("models/imagenet_class_index_extended.json", "r", encoding="utf-8") as f:
    class_index = json.load(f)

id_to_label = {int(k): v for k, v in class_index.items()}

def decode_1001(preds, top=5):
    top_indices = preds[0].argsort()[-top:][::-1]
    decoded = [(i, id_to_label.get(i, "Unknown"), float(preds[0][i])) for i in top_indices]
    return [decoded]

def load_mnv2_custom(weights=None):
    return load_model("models/mnv2_1001_person.keras")


# --- 5クラス用のラベルマップと関数（統一済み） ---
with open("models/class_index_5class.json", "r", encoding="utf-8") as f:
    class_index_5class = json.load(f)

id_to_label_5class = {int(k): v for k, v in class_index_5class.items()}

def decode_5class(preds, top=1):
    top_indices = preds[0].argsort()[-top:][::-1]
    decoded = [(i, id_to_label_5class.get(i, "Unknown"), float(preds[0][i])) for i in top_indices]
    return [decoded]

def load_5class_model(weights=None):
    return load_model("models/effb0_5class_model.keras")
