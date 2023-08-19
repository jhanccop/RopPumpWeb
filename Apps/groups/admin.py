from django.contrib import admin
from .models import Group
# Register your models .

class configField(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreated.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 

	list_display = ('GroupName','Company','DateCreatedFormat')
	list_filter = ('Company', 'GroupName')

admin.site.register(Group, configField)