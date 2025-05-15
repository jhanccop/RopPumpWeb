from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import(
    infoRequests,
)

## ==================== CONTACTOS DE INTERES =====================
class infoRequestsResource(resources.ModelResource):
    class Meta:
        model = infoRequests

@admin.register(infoRequests)
class infoRequestsAdmin(ImportExportModelAdmin):
	resource_class = infoRequestsResource

	list_display = (
		'id',
		'DateCreate',
		'Name',
		'LastName',
        'Interes',
		'Email',
		'Organization',
    )
	search_fields = ('Organization','Interes')
	list_filter = ('Organization','Interes')
