from django.views import View
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import(PasswordChangeView, PasswordChangeDoneView,
                                     PasswordResetView, PasswordResetDoneView,
                                     PasswordResetConfirmView, PasswordResetCompleteView) 
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode
# from django.core.signing import dumps, loads, BadSignature, SignatureExpired
# from django.contrib.sites.shortcuts import get_current_site

from .forms import (SignUpForm,  EmailChangeRequestForm,
                     EmailChangeConfirmForm,)


User = get_user_model()

# 会員登録画面
class SignUpView(CreateView):
    template_name = 'accounts/signup/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('accounts:signup_pre')
    # CreateViewを継承しているためtemplate_nameで十分
    # form_class 今回はカスタム 
    # success_url ログイン後のリダイレクト先
    # reverse_lazy urls指定の名前からジャンプ

    # form_valid 入力が正しく為された時に動作
    # mailがuserとして与えられる
    def form_valid(self, form):
        """仮登録と本登録用メールの送信"""
        user = form.save(commit=False)
        user.is_active = False
        user.save()
            #activeではないユーザーとしてsave
            #formがカスタムなためここで設定
        """
         # アクティベーションURLを生成
         # こちらは脆弱であるためコメントアウト
        current_site = get_current_site(self.request)
        context = {
            'protocol': self.request.scheme, # http or httpsを判定
            'domain': current_site.domain, # URLからdomainを取得
            'token': dumps(user.pk), # PrimaryKeyをDumpsでトークンに変換
            'user': user,
        }
        """

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
            # force_bytes()：整数（pkなど）をバイト列に変換
            # urlsafe_base64_encode()：そのバイト列を文字列へ変換
            # default_token_generator.make_token トークンを生成
            # パスワードリセットなどでも使われる堅牢な仕組み

        activation_url = self.request.build_absolute_uri(
            reverse('accounts:activate', kwargs={
                'uidb64': uid,
                'token': token,
            })
        )
            # request.build_absolute_uri 相対URLから絶対URLに変換
            # reverse urlsを参考にURLを作成
        context = {
            'activation_url': activation_url,
            'user': user,
        }        

        # contextとsubject、messageを使い文面を作成
        # render_to_string txtにcontextを送り込む
        subject = render_to_string('mail/activation/subject.txt', context)
        message = render_to_string('mail/activation/message.txt', context)

        #EmailMessageでメール形態データを作成できる
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="no-reply@picanalyzer.net",
            to=[user.email],
        )
        email.send()
        return redirect('accounts:signup_pre')  # 仮登録完了画面へ

# 本登録操作
class ActivateView(View):
    #urlsでtoken指定位置から引数を取得
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
                # urlsafe_base64_decode 文字列からバイトに戻す
                # .decode バイトからstrに戻す
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return redirect("accounts:url_invalid")

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect("accounts:signup_done")
        else:
            return redirect("accounts:url_invalid")
    """
    こちらはdumpsに対応する形
    def get(self, request, token):
        try:
            user_pk = loads(token, max_age=60*60*24)  # 60秒*60分*24時間で1日の意
            user = get_object_or_404(get_user_model(), pk=int(user_pk))
        except (BadSignature, SignatureExpired, get_user_model().DoesNotExist):
            return redirect("accounts:url_invalid")
        #dumpsした内容をloadsで復元
        #get_object_or_404は前者に後者を引数として与え結果を出力

        user.is_active = True
        user.save()
        login(request, user)
        return redirect("accounts:signup_done")
    """

# 仮登録完了通知
class SignUpPreDoneView(TemplateView):
    template_name = 'accounts/signup/signup_pre.html'
    #template_name は文字だけのページを用意する場合に重宝

# 本登録完了通知
class SignUpDoneView(TemplateView):
    template_name = 'accounts/signup/signup_done.html'

# URLエラー時に遷移
class UrlInvalidView(TemplateView):
    template_name = 'accounts/url_invalid.html'

# パスワードリセット画面
class _PasswordResetView(PasswordResetView):
    template_name = 'accounts/password/password_reset_form.html'
    subject_template_name = 'mail/reset/subject.txt'
    email_template_name = 'mail/reset/message.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    # 継承で必要情報だけで完了

# パスワードリセットメール送信完了
class _PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password/password_reset_done.html'

# 新規パスワード入力
class _PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'accounts/password/password_reset_confirm.html'

# パスワード変更完了通知
class _PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password/password_reset_complete.html'

# パスワード変更画面
class _PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'accounts/password/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_name"] = "password_change"
        return context

# パスワード変更完了画面
class _PasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'accounts/password/password_change_done.html'


# メールアドレス変更画面
class EmailChangeRequestView(LoginRequiredMixin, View):
    def get(self, request):
        form = EmailChangeRequestForm()
        return render(request, 'accounts/email/email_change_request.html', {'form': form})

    def post(self, request):
        form = EmailChangeRequestForm(request.POST)

        if form.is_valid(): #formが有効であるなら
            new_email = form.cleaned_data['email'] #is_valid()後に有効な正しいデータ
            uid = urlsafe_base64_encode(force_bytes(request.user.pk))
            token = default_token_generator.make_token(request.user)
            confirm_url = request.build_absolute_uri(
                reverse('accounts:email_change_confirm', kwargs={
                    'uidb64': uid,
                    'token': token,
                }) + f'?email={new_email}'
            )
            context = {
                'user': request.user,
                'new_email': new_email,
                'confirm_url': confirm_url,
            }

            subject = render_to_string('mail/email_change/subject.txt', context)
            message = render_to_string('mail/email_change/message.txt', context)

            email = EmailMessage(
                subject=subject.strip(),
                body=message,
                from_email="no-reply@picanalyzer.net",
                to=[new_email],
            )
            email.send()
            messages.success(request, "確認メールを送信しました。新しいメールをご確認ください。")
            return redirect('accounts:email_change_request')

        return render(request, 'accounts/email/email_change_request.html', {'form': form})


#メールアドレス変更パスワード確認
class EmailChangeConfirmView(LoginRequiredMixin, View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            # urlsafe_base64_decode 文字列からバイトに戻す
            # .decode バイトからstrに戻す
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            new_email = request.GET.get('email')
            form = EmailChangeConfirmForm()
            return render(request, 'accounts/email/email_change_confirm.html', {
                'form': form,
                'new_email': new_email,
            })
        else:
            return redirect('accounts:url_invalid')

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        form = EmailChangeConfirmForm(request.POST)
        new_email = request.GET.get('email')

        if user and default_token_generator.check_token(user, token):
            if form.is_valid() and user.check_password(form.cleaned_data['password']):
                user.email = new_email
                user.save()
                messages.success(request, "メールアドレスを更新しました。")
                return redirect('accounts:email_change_request')
            else:
                messages.error(request, "パスワードが正しくありません。")

        return render(request, 'accounts/email/email_change_confirm.html', {
            'form': form,
            'new_email': new_email,
        })

# メールアドレス変更確定
class EmailChangeCompleteView(TemplateView):
    template_name = 'accounts/email/email_change_complete.html'

# ユーザーページ
class UserInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/user_info.html'



signup = SignUpView.as_view()
activate = ActivateView.as_view()
signup_pre = SignUpPreDoneView.as_view()
signup_done = SignUpDoneView.as_view()
url_invalid = UrlInvalidView.as_view()

password_reset = _PasswordResetView.as_view()
password_reset_done = _PasswordResetDoneView.as_view()
password_reset_confirm = _PasswordResetConfirmView.as_view()
password_reset_complete = _PasswordResetCompleteView.as_view()

password_change = _PasswordChangeView.as_view()
password_change_done = _PasswordChangeDoneView.as_view()

email_change_request = EmailChangeRequestView.as_view()
email_change_confirm = EmailChangeConfirmView.as_view()
email_change_complete = EmailChangeCompleteView.as_view()

user_info = UserInfoView.as_view()

