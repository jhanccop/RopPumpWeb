from django.contrib import admin

from .models import (
    TankDevice,
	WellAnalyzerDevice,
	EnvironmentalDevice,
	CamVidDevice,
	Gateway,
	TrapView
)

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

class confCamVidDevice(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = (
		'id',
		'DeviceName',
		'IdVisualSamplingPoint',
		'DeviceMacAddress',
		'TimeStart',
		'TimeEnd',
		'SleepTime',
		'is_continous',
		'refresh')
	list_filter = ('IdVisualSamplingPoint',)
admin.site.register(CamVidDevice, confCamVidDevice)

class confGateway(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = (
		'id',
		'Owner',
		'DeviceName',
		'DeviceMacAddress',
		'TimeStart',
		'TimeEnd',
		'SleepTime',
		'refresh')
	list_filter = ('Owner',)
admin.site.register(Gateway, confGateway)

class confTrapView(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = (
		'id',
		'IdGateway',
		'Owner',
		'DeviceName',
		'DeviceMacAddress',
		'A_TH',
		'A_WS',
		)
	list_filter = ('Owner',)
admin.site.register(TrapView, confTrapView)
