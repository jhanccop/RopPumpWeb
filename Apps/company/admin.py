from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Company

## ==================== COMPANY DATE =====================
class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
	resource_class = CompanyResource

	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreate'
	DateCreatedFormat.short_description = 'Date Create'

	list_display = (
        'id',
		'CompanyName',
		'LocationState',
		'LocationCounty',
		'DateCreate',
		'CompanyType',
    )
	search_fields = ('CompanyType',)
	list_filter = ('CompanyType',)

