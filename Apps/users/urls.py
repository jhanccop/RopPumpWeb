from django.urls import path
from . import views

app_name = "user_app"

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user-register'),
    path('login/', views.LoginUser.as_view(), name='user-login'),
    path('logout/', views.LogoutView.as_view(), name='user-logout'),
    path('no-access/', views.NoAccessView.as_view(), name='no_access'),

    # Admin panel
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/users/', views.UserListView.as_view(), name='user_list'),
    path('admin-panel/users/new/', views.UserCreateView.as_view(), name='user_create'),
    path('admin-panel/users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('admin-panel/users/<int:pk>/toggle/', views.UserToggleActiveView.as_view(), name='user_toggle'),
    path('admin-panel/companies/', views.CompanyListView.as_view(), name='company_list'),
    path('admin-panel/companies/new/', views.CompanyCreateView.as_view(), name='company_create'),
    path('admin-panel/companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_update'),
]
