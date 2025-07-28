from django.urls import path
from .views import (UsersManagerView, UserEditView, UserEditConfirmView,
                     UserDeleteView, PicturesManagerView, ImageDeleteView,)

app_name = 'adminpanel'

urlpatterns = [
    # ユーザー管理画面（一覧）
    path('users/', UsersManagerView.as_view(), name='users_manager'),

    # ユーザー編集画面
    path('users/<int:user_id>/edit/', UserEditView.as_view(), name='user_edit'),

    # 編集内容確認画面
    path('users/edit/confirm/', UserEditConfirmView.as_view(), name='user_edit_confirm'),

    # ユーザー削除確認画面
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # 画像解析管理画面（全ユーザー分）
    path('pictures/', PicturesManagerView.as_view(), name='pictures_manager'),

    # 画像削除画面
    path('pictures/<int:image_id>/delete/', ImageDeleteView.as_view(), name='image_delete'),
]