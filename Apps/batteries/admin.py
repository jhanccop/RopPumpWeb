from django.contrib import admin

from .models import Battery

class configBattery(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreated.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 

	list_display = ('BatteryName','Company','DateCreatedFormat')
	list_filter = ('Company', 'BatteryName')

admin.site.register(Battery, configBattery)