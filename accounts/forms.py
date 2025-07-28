from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import MstUsers



class SignUpForm(UserCreationForm):
    class Meta:
        model = MstUsers
        fields = ("email",) 

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # アクティブでないユーザーが存在する場合は削除して再利用可能に
        try:
            existing = MstUsers.objects.get(email=email)
            if not existing.is_active:
                existing.delete()
            else:
                raise forms.ValidationError("この Email を持ったユーザーは既に存在します。")
        except MstUsers.DoesNotExist:
            pass  # 問題なし
        return email


class EmailChangeRequestForm(forms.Form):
    email = forms.EmailField(label="Email:", max_length=255)


class EmailChangeConfirmForm(forms.Form):
    password = forms.CharField(
        label="PASSWORD:",
        widget=forms.PasswordInput,
        strip=False,
    )
