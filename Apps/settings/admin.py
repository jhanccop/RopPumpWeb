from django.contrib import admin

# Register your models here.

from .models import setting

class confSetting(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreated.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('PumpName','DateCreatedFormat','Available','MacAddress','Refresh','Status','TimeOn','TimeOff','ThresholdAlert1','ThresholdAlert2','ThresholdStop')
	list_filter = ('Available','Status')
admin.site.register(setting, confSetting)