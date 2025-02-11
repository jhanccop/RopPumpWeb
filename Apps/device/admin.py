from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    TankDevice,
	WellAnalyzerDevice,
	EnvironmentalDevice,
	CamVidDevice,
	Gateway,
	TrapView,
	WeatherStation
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
		'IdLocation',
		'DeviceName',
		'DeviceMacAddress',
		'TimeStart',
		'TimeEnd',
		'SleepTime',)
	list_filter = ('IdLocation',)
admin.site.register(Gateway, confGateway)

## ==================== Wheather station =====================
class WeatherStationResource(resources.ModelResource):
    class Meta:
        model = WeatherStation

@admin.register(WeatherStation)
class WeatherStationAdmin(ImportExportModelAdmin):
	resource_class = WeatherStationResource

	list_display = (
        'id',
		'DeviceName',
		'DeviceMacAddress',
		'IdLocation',
		'IdGateway',
		'A_TH',
		'A_WP',
		'A_RS',
		'SleepTime',
    )
	search_fields = ('IdLocation',)
	list_filter = ('IdLocation',)

## ==================== TRAPVIEW =====================
class TrapViewResource(resources.ModelResource):
    class Meta:
        model = TrapView

@admin.register(TrapView)
class TrapViewAdmin(ImportExportModelAdmin):
	resource_class = TrapViewResource

	list_display = (
        'id',
		'DeviceName',
		'DeviceMacAddress',
		'A_TH',
		'TimeStart',
		'TimeEnd',
		'SleepTime',
		'IdLocation',
		'IdGateway',
    )
	search_fields = ('IdLocation',)
	list_filter = ('IdLocation',)

