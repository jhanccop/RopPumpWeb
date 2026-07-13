from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse

from django.views.generic import (
    View,
    CreateView,
    ListView,
    UpdateView,
    TemplateView,
)

from django.views.generic.edit import FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UserRegisterForm, LoginForm
from .models import User, Application
from Apps.company.models import Company


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/'

    def form_valid(self, form):
        User.objects.create_user(
            form.cleaned_data['UserName'],
            form.cleaned_data['Email'],
            form.cleaned_data['password1'],
            Name=form.cleaned_data['Name'],
            LastName=form.cleaned_data['LastName'],
            CompanyId=form.cleaned_data.get('CompanyId'),
        )
        return super(UserRegisterView, self).form_valid(form)


class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        login(self.request, user)
        return super(LoginUser, self).form_valid(form)

    def get_success_url(self):
        return self.request.user.get_first_app_url()


class LogoutView(View):
    def get(self, request, *args, **kargs):
        logout(request)
        return HttpResponseRedirect(reverse('home_app:home'))


# ─── Permission mixins (local import to avoid circular) ───────────────────────
from .mixins import AdminRequiredMixin, SuperAdminRequiredMixin


# ─── Access denied ────────────────────────────────────────────────────────────
class NoAccessView(TemplateView):
    template_name = 'users/no_access.html'


# ─── Admin dashboard ──────────────────────────────────────────────────────────
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'users/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_superadmin:
            context['total_users'] = User.objects.count()
            context['total_companies'] = Company.objects.count()
            context['active_users'] = User.objects.filter(IsActive=True).count()
        else:
            company = user.CompanyId
            context['total_users'] = User.objects.filter(CompanyId=company).count()
            context['active_users'] = User.objects.filter(CompanyId=company, IsActive=True).count()
        context['applications'] = Application.objects.all()
        return context


# ─── User management ──────────────────────────────────────────────────────────
class UserListView(AdminRequiredMixin, ListView):
    template_name = 'users/admin/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = User.objects.select_related('CompanyId').prefetch_related('Applications')
        if not self.request.user.is_superadmin:
            qs = qs.filter(CompanyId=self.request.user.CompanyId)
        return qs.order_by('CompanyId__CompanyName', 'UserName')


class UserCreateView(AdminRequiredMixin, CreateView):
    template_name = 'users/admin/user_form.html'
    model = User
    success_url = reverse_lazy('user_app:user_list')

    def get_form_class(self):
        from .forms import UserAdminForm
        return UserAdminForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        form.save_m2m()
        messages.success(self.request, f'Usuario {user.UserName} creado exitosamente.')
        return redirect(self.success_url)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'users/admin/user_form.html'
    model = User
    success_url = reverse_lazy('user_app:user_list')

    def get_form_class(self):
        from .forms import UserAdminEditForm
        return UserAdminEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado.')
        return super().form_valid(form)


class UserToggleActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        target = User.objects.get(pk=pk)
        if not request.user.is_superadmin and target.CompanyId != request.user.CompanyId:
            return JsonResponse({'ok': False}, status=403)
        target.IsActive = not target.IsActive
        target.save()
        return redirect('user_app:user_list')


# ─── Company management ───────────────────────────────────────────────────────
class CompanyListView(SuperAdminRequiredMixin, ListView):
    template_name = 'users/admin/company_list.html'
    context_object_name = 'companies'
    queryset = Company.objects.order_by('CompanyName')


class CompanyCreateView(SuperAdminRequiredMixin, CreateView):
    template_name = 'users/admin/company_form.html'
    model = Company
    success_url = reverse_lazy('user_app:company_list')

    def get_form_class(self):
        from .forms import CompanyAdminForm
        return CompanyAdminForm


class CompanyUpdateView(SuperAdminRequiredMixin, UpdateView):
    template_name = 'users/admin/company_form.html'
    model = Company
    success_url = reverse_lazy('user_app:company_list')

    def get_form_class(self):
        from .forms import CompanyAdminForm
        return CompanyAdminForm
