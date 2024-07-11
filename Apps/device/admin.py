from django.contrib import admin

from .models import TankDevice, WellAnalyzerDevice, EnvironmentalDevice

class confAnalyzerData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('id','DeviceName','DateCreatedFormat','DeviceMacAddress', 'DeviceStatus','SamplingRate','IdRodPumpWell')
	list_filter = ('DeviceStatus','IdRodPumpWell')
admin.site.register(WellAnalyzerDevice, confAnalyzerData)

class confEnvironmentalDevice(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('id','DeviceName','DateCreatedFormat', 'DeviceMacAddress','DeviceStatus','SamplingRate','IdEnvironmental')
	list_filter = ('DeviceStatus','IdEnvironmental')
admin.site.register(EnvironmentalDevice, confEnvironmentalDevice)

class confTankDevice(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('id','DeviceName','DateCreatedFormat', 'DeviceMacAddress','DeviceStatus','SamplingRate','IdTank')
	list_filter = ('DeviceStatus','IdTank')
admin.site.register(TankDevice, confTankDevice)

