from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import (SignUpView, SignUpPreDoneView, ActivateView,
                    UrlInvalidView, SignUpDoneView,
                    _PasswordResetView, _PasswordResetDoneView, _PasswordResetConfirmView,
                    _PasswordResetCompleteView, _PasswordChangeView, _PasswordChangeDoneView,
                    EmailChangeRequestView, EmailChangeConfirmView, EmailChangeCompleteView,
                    UserInfoView,)


app_name = "accounts"

urlpatterns = [
    # ログイン・ログアウト
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    
    # 会員登録
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signup/pre/", SignUpPreDoneView.as_view(), name="signup_pre"),
    path("signup/done/", SignUpDoneView.as_view(), name="signup_done"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="activate"),
    path("invalid/", UrlInvalidView.as_view(), name="url_invalid"),

    # パスワードリセット
    path('password_reset/', _PasswordResetView.as_view(), name='password_reset'), 
    path('password_reset/done/', _PasswordResetDoneView.as_view(), name='password_reset_done'), 
    path('reset/<uidb64>/<token>/', _PasswordResetConfirmView.as_view(), name='password_reset_confirm'), 
    path('reset/done/', _PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # パスワード変更
    path('password_change/', _PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', _PasswordChangeDoneView.as_view(), name='password_change_done'),

    # メールアドレス変更
    path('email_change/', EmailChangeRequestView.as_view(), name='email_change_request'),
    path('email_change/<uidb64>/<token>/', EmailChangeConfirmView.as_view(), name='email_change_confirm'),
    path('email_change/done/', EmailChangeCompleteView.as_view(), name='email_change_complete'), 

    # 会員情報
    path('info/', UserInfoView.as_view(), name='user_info'),
]
