from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class AppAccessMixin(LoginRequiredMixin):
    """Add required_app = 'oilfield'|'fauna'|'transformadores' to any view."""
    required_app = None
    login_url = reverse_lazy('user_app:user-login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_app and not request.user.has_app_access(self.required_app):
            return redirect('user_app:no_access')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Require admin or superadmin role."""
    login_url = reverse_lazy('user_app:user-login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return redirect('user_app:no_access')
        return super().dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('user_app:user-login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superadmin:
            return redirect('user_app:no_access')
        return super().dispatch(request, *args, **kwargs)
