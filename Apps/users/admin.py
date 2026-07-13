from django.contrib import admin
from .models import User, Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('Code', 'Name', 'DashboardUrl', 'IsActive')
    list_editable = ('IsActive',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('UserName', 'Name', 'LastName', 'CompanyId', 'Role', 'IsActive', 'is_staff')
    list_filter = ('Role', 'IsActive', 'CompanyId')
    search_fields = ('UserName', 'Email', 'Name')
    filter_horizontal = ('Applications', 'groups', 'user_permissions')
