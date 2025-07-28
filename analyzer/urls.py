from django.urls import path
from .views import TopView, UploadAnalyzeView, ReanalyzeView
#from django.conf import settings
#from django.conf.urls.static import static

app_name = "analyzer"

urlpatterns =[
    # トップページ
    path("", TopView.as_view(), name="top"),

    # アップロード画面
    path("upload/", UploadAnalyzeView.as_view(), name="upload"),

    # 再解析ページ
    path('reanalyze/<int:analysis_id>/', ReanalyzeView.as_view(), name='reanalyze'),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

