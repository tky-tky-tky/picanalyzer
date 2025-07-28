from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from PIL import Image
import os, tempfile

from .models import TransAnalysis
from .tasks import analyze_image_task, save_image_and_analyze_task # Celeryタスクをimport



class TopView(LoginRequiredMixin, TemplateView):
    template_name = 'analyzer/top.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 絞り込みとソートパラメータ取得 
        selected_status = self.request.GET.get('status')
        selected_label = self.request.GET.get('label')
        sort_order = self.request.GET.get('sort', 'desc')

        # 絞り込み条件作成
        filters = Q(image__user=self.request.user)
        if selected_status:
            filters &= Q(status=selected_status)
        if selected_label:
            filters &= Q(label=selected_label)

        # 並び順（降順がデフォルト）
        sort_field = 'image__uploaded_at'
        if sort_order == 'asc':
            order_by = sort_field
        else:
            order_by = f'-{sort_field}'

        # 対象データ取得
        analyses = (
            TransAnalysis.objects
            .filter(filters)
            .select_related('image')
            .order_by(order_by)
        )

        # 「準備中」の順番算出
        waiting_list = list(
            TransAnalysis.objects
            .filter(status="準備中")
            .order_by('image__uploaded_at')
            .values_list('analysis_id', flat=True)
        )
        waiting_position = {aid: idx + 1 for idx, aid in enumerate(waiting_list)}

        for analysis in analyses:
            if analysis.status == "準備中":
                analysis.waiting_number = waiting_position.get(analysis.analysis_id, None)
            else:
                analysis.waiting_number = None

        # ラベル一覧を自動生成（フィルタに使用）
        all_labels = (
            TransAnalysis.objects
            .filter(image__user=self.request.user)
            .exclude(label__isnull=True)
            .exclude(label__exact="")
            .values_list('label', flat=True)
            .distinct()
        )

        context.update({
            'analyses': analyses,
            'selected_status': selected_status,
            'selected_label': selected_label,
            'sort_order': sort_order,
            'label_options': all_labels,
        })
        return context



class UploadAnalyzeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "analyzer/upload.html")

    def post(self, request):
        image_files   = request.FILES.getlist("images")
        model_name    = request.POST.get("model", "mobilenet_v2")
        use_category  = bool(request.POST.get("use_category"))   # チェック有無

        # 画像なし
        if not image_files:
            messages.error(request, "Please select at least one image.")
            return render(request, "analyzer/upload.html")

        # 4 枚以上
        if len(image_files) > 3:
            messages.error(request, "You can upload up to 3 images.")
            return render(request, "analyzer/upload.html")

        valid_images = []
        for f in image_files:
            try:
                Image.open(f).verify() # verify=画像が壊れていないか調べる
                f.seek(0) # 画像の読み込み位置を初期化(セーフティ)
                valid_images.append(f)
            except Exception:
                continue

        if not valid_images:
            return render(request, "analyzer/upload.html",
                          {"error": "No valid image files were found."})

        # Celeryへ投入（全て非同期）
        for img_file in valid_images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(img_file.name)[1]) as tmp:
                for chunk in img_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Celeryタスク呼び出し
            save_image_and_analyze_task.delay(
                tmp_path,
                request.user.id,
                model_name,
                use_category
            )

        return redirect("analyzer:top")


class ReanalyzeView(View):
    def get(self, request, analysis_id):
        analysis = get_object_or_404(TransAnalysis, pk=analysis_id)
        return render(request, "analyzer/reanalyze.html", {"analysis": analysis})

    def post(self, request, analysis_id):
        analysis = get_object_or_404(TransAnalysis, pk=analysis_id)

        # フォームからの新しい値を反映
        model_name = request.POST.get("model_name")
        use_category = bool(request.POST.get("use_category"))

        analysis.model_name = model_name
        analysis.use_category = use_category

        # ステータスと関連情報を初期化（画像は保持）
        analysis.status = '準備中'
        analysis.label = None
        analysis.reliability = None
        analysis.started_at = None
        analysis.ended_at = None
        analysis.error_name = None
        analysis.error_log = None
        analysis.save()

        # Celeryへ再解析を依頼
        image_url = analysis.image.image.url

        analyze_image_task.delay(
            analysis_id=analysis.analysis_id,
            full_path=image_url,
            model_name=analysis.model_name,
            use_category=analysis.use_category
        )

        return redirect("analyzer:top")

top = TopView.as_view()
upload = UploadAnalyzeView.as_view()
reanalyze = ReanalyzeView.as_view()

