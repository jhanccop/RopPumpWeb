from django.contrib import admin

# Register your models here.
#from django.contrib import admin

from .models import RodPumpData, TankData

class confRPData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('PumpName','DateCreatedFormat','PumpFill', 'Diagnosis','Recomendation')
	list_filter = ('Diagnosis',)
admin.site.register(RodPumpData, confRPData)


class confTankData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('TankName','DateCreatedFormat', 'OilLevel','WaterLevel','Status')
	list_filter = ('Status',)
admin.site.register(TankData, confTankData)
