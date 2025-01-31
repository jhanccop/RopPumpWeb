from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
  Location,
)
## ==================== Location =====================
class LocationResource(resources.ModelResource):
    class Meta:
        model = Location

@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource
    
    list_display = (
        'id',
        'LocationName',
        'Field',
    )
    
    search_fields = ('Field',)
    list_filter = ('Field',)
