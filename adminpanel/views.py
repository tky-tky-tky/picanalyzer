from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

from accounts.models import MstUsers
from analyzer.models import MstImages, TransAnalysis


class PicturesManagerView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'adminpanel/pictures_manager.html'

    # UserPassesTestMixin,test_funcでアクセス権限を確認
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # フィルタ取得
        selected_user = self.request.GET.get('user')
        selected_status = self.request.GET.get('status')
        selected_error = self.request.GET.get('error')
        selected_model = self.request.GET.get('model')
        sort_order = self.request.GET.get('sort', 'desc')

        # フィルタ構築
        filters = Q()
        if selected_user:
            filters &= Q(image__user__email=selected_user)
        if selected_status:
            filters &= Q(status=selected_status)
        if selected_error:
            filters &= Q(error_name=selected_error)
        if selected_model:
            filters &= Q(model_name=selected_model)

        order_field = 'image__uploaded_at'
        order_by = order_field if sort_order == 'asc' else f'-{order_field}'

        # データ取得
        analyses = (
            TransAnalysis.objects
            .filter(filters)
            .select_related('image', 'image__user')
            .order_by(order_by)
        )

        # 準備中の順番算出
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

        # プルダウン選択肢用
        all_users = MstUsers.objects.filter(is_active=True).values_list('email', flat=True).distinct()
        all_errors = (
            TransAnalysis.objects
            .exclude(error_name__isnull=True)
            .exclude(error_name__exact="")
            .values_list('error_name', flat=True)
            .distinct()
        )
        all_models = (
            TransAnalysis.objects
            .values_list('model_name', flat=True)
            .distinct()
        )

        context.update({
            'analyses': analyses,
            'selected_user': selected_user,
            'selected_status': selected_status,
            'selected_error': selected_error,
            'selected_model': selected_model,
            'sort_order': sort_order,
            'user_options': all_users,
            'error_options': all_errors,
            'model_options': all_models,
        })
        return context


class UsersManagerView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'adminpanel/users_manager.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 絞り込み＆ソートパラメータ取得
        selected_staff = self.request.GET.get('is_staff')
        sort_order = self.request.GET.get('sort', 'desc')

        # 絞り込み構築
        filters = Q()
        if selected_staff in ['True', 'False']:
            filters &= Q(is_staff=(selected_staff == 'True'))

        # ソート条件
        order_field = 'created_at'
        order_by = order_field if sort_order == 'asc' else f'-{order_field}'

        # ユーザー一覧取得
        users = MstUsers.objects.filter(filters).order_by(order_by)

        # コンテキストに渡す
        context.update({
            'users': users,
            'selected_staff': selected_staff,
            'sort_order': sort_order,
        })
        return context

class UserEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'adminpanel/user_edit.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, user_id):
        user = get_object_or_404(MstUsers, user_id=user_id)
        return render(request, self.template_name, {
            'user_obj': user
        })

    def post(self, request, user_id):
        user = get_object_or_404(MstUsers, user_id=user_id)

        new_email = request.POST.get('email', '').strip()
        new_username = request.POST.get('username', '').strip()
        new_is_staff = request.POST.get('is_staff', '') == 'True'

        if (
            new_email == user.email and
            new_username == (user.username or '') and
            new_is_staff == user.is_staff
        ):
            messages.info(request, "内容が変更されていません。")
            return render(request, self.template_name, {
                'user_obj': user
            })

        # セッションに仮保存（確認画面に渡す用）
        request.session['edit_user'] = {
            'user_id': user.user_id,
            'email': new_email,
            'username': new_username,
            'is_staff': new_is_staff,
        }
        return redirect('adminpanel:user_edit_confirm')
    
class UserEditConfirmView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'adminpanel/user_edit_confirm.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        edit_data = request.session.get('edit_user')
        if not edit_data:
            return redirect('adminpanel:users_manager')

        return render(request, self.template_name, {
            'edit_user': edit_data
        })

    def post(self, request):
        edit_data = request.session.get('edit_user')
        if not edit_data:
            return redirect('adminpanel:users_manager')

        user = get_object_or_404(MstUsers, user_id=edit_data['user_id'])
        user.email = edit_data['email']
        user.username = edit_data['username']
        user.is_staff = edit_data['is_staff']
        user.save()

        # セッション削除 & リダイレクト
        del request.session['edit_user']
        return redirect('adminpanel:users_manager')
    


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'adminpanel/user_delete.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, user_id):
        user = get_object_or_404(MstUsers, user_id=user_id)
        return render(request, self.template_name, {'user_obj': user})

    def post(self, request, user_id):
        user = get_object_or_404(MstUsers, user_id=user_id)
        user.delete()  # MstImages, TransAnalysisもCASCADEで一括削除される
        return redirect('adminpanel:users_manager')

class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'adminpanel/image_delete_confirm.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, image_id):
        # MstImagesを取得
        image = get_object_or_404(MstImages, image_id=image_id)
        # その画像に紐づくTransAnalysisを取得
        analysis = get_object_or_404(TransAnalysis, image=image)
        return render(request, self.template_name, {'analysis': analysis})

    def post(self, request, image_id):
        # MstImagesを取得
        image = get_object_or_404(MstImages, image_id=image_id)
        # 削除（TransAnalysisもCASCADEで削除）
        image.delete()
        return redirect('adminpanel:pictures_manager')

users_manager = UsersManagerView.as_view()
user_edit = UserEditView.as_view()
user_edit_confirm = UserEditConfirmView.as_view()
user_delete = UserDeleteView.as_view()
pictures_manager = PicturesManagerView.as_view()
image_delete = ImageDeleteView.as_view()
