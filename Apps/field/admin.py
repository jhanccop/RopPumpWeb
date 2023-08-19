from django.contrib import admin

from .models import Field
# Register your models .

class configField(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreated.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 

	list_display = ('FieldName','Company','LocationState','LocationCounty','DateCreatedFormat')
	list_filter = ('Company', 'FieldName')

admin.site.register(Field, configField)
