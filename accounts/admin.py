from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import MstUsers


class CustomUserAdmin(BaseUserAdmin):
    model = MstUsers

    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_superuser')
    ordering = ('created_at',)
    search_fields = ('email', 'username')


    #編集画面のフィールド
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('ユーザー情報', {'fields': ('username',)}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('その他', {'fields': ('last_login',)}),
    )

    #ユーザー新規登録時のフォームで表示されるフィールド
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )


admin.site.register(MstUsers, CustomUserAdmin)  # Userモデルを登録
admin.site.unregister(Group)  # Groupモデルは不要のため非表示にします