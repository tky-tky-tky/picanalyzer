from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import MstUsers


class MstImages(models.Model):
    image_id = models.AutoField(verbose_name=_("image_id"), primary_key=True)
    user = models.ForeignKey(MstUsers, verbose_name=_("user"), on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_("image"), upload_to='uploads/')
    uploaded_at = models.DateTimeField(verbose_name=_("uploaded_at"), auto_now_add=True)

    def __str__(self):
        return f"{self.image_id}({self.image.name})"

    class Meta:
        verbose_name = _("Mst Image")
        verbose_name_plural = _("Mst Images")


class TransAnalysis(models.Model):
    S_CHOICES = [
        ("準備中", "準備中"),
        ("解析中", "解析中"),
        ("成功", "解析成功"),
        ("失敗", "解析失敗"),
    ]

    analysis_id = models.AutoField(verbose_name=_("analysis_id"), primary_key=True)
    image = models.ForeignKey(MstImages, verbose_name=_("image"), on_delete=models.CASCADE)
    model_name = models.CharField(verbose_name=_("model_name"), max_length=20)
    use_category = models.BooleanField(verbose_name=_("use_category"), default=False)

    status = models.CharField(verbose_name=_("status"), max_length=10,
                              choices=S_CHOICES, default="準備中")
    label = models.CharField(verbose_name=_("label"), max_length=20, null=True)
    top_preds = models.JSONField(verbose_name=_("top_predictions"),null=True, blank=True,)
    reliability = models.FloatField(verbose_name=_("reliability"), null=True)

    started_at = models.DateTimeField(verbose_name=_("started_at"), null=True)
    ended_at = models.DateTimeField(verbose_name=_("ended_at"), null=True)

    error_log = models.TextField(verbose_name=_("error_log"), null=True)
    error_name = models.CharField(verbose_name=_("error_name"), max_length=20, null=True)

    def __str__(self):
        return f"{self.analysis_id}({self.image.image.name[:20]})"

    class Meta:
        verbose_name = _("Trans Analysis")
        verbose_name_plural = _("Trans Analyses")