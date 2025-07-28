from django.db import models
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _ #多言語対応
from django.core.mail import send_mail

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['is_active'] = True
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class MstUsers(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(verbose_name=_("user_id"), primary_key=True)
    username = models.CharField(verbose_name=_("username"), max_length=10, null=True, blank=True)
    email = models.EmailField(verbose_name=_("email"), unique=True)
    is_active = models.BooleanField(verbose_name=_("is_active"), default=False)
    is_superuser= models.BooleanField(verbose_name=_("is_superuser"), default=False)
    is_staff = models.BooleanField(verbose_name=_("is_staff"), default=False)
    created_at = models.DateTimeField(verbose_name=_("created_at"), auto_now_add=True)


    USERNAME_FIELD = "email" # ログイン時、ユーザー名の代わりにemailを使用
    REQUIRED_FIELDS = []  # スーパーユーザー作成時に必須項目に設定

    objects = UserManager()  
    
    def __str__(self):
        return self.email
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        #ユーザーにメールを送信する簡単な方法
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    class Meta:
        verbose_name = _("Mst User")
        verbose_name_plural = _("Mst Users")

