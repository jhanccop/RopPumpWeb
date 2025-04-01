from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import(
    RodPumpData,
	TankData,
	EnvironmentalData,
	CamVidData,
	TrapViewData,
	GatewayData,
	WeatherStationData
)

## ==================== RodPumpData =====================
class RodPumpDataResource(resources.ModelResource):
    class Meta:
        model = RodPumpData

@admin.register(RodPumpData)
class RodPumpDataDataAdmin(ImportExportModelAdmin):
	resource_class = RodPumpDataResource

	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreate'
	DateCreatedFormat.short_description = 'Date Create'

	list_display = (
		'id',
        'IdDevice',
		'DateCreatedFormat',
		'PumpFillage',
		'Diagnosis',
		'Recomendation',
		'SPM',
		'Status',
    )
	search_fields = ('IdDevice',)
	list_filter = ('IdDevice',)

"""class confRPData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('IdDevice','DateCreatedFormat','PumpFillage', 'Diagnosis','Recomendation')
	#list_filter = ('Diagnosis','IdDevice')
admin.site.register(RodPumpData, confRPData)"""

class confTankData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('IdDevice','DateCreatedFormat', 'Level','Temperature','Status')
	list_filter = ('Status','IdDevice')
admin.site.register(TankData, confTankData)

class confEnvironmentalData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('IdDevice',
					'DateCreatedFormat',
					'Humidity1',
					'Temperature1',
					'AtmosphericPressure1',
					'Humidity2',
					'Temperature2',
					'AtmosphericPressure2',
					'Status'
					)
	list_filter = ('Status','IdDevice')
admin.site.register(EnvironmentalData, confEnvironmentalData)

class confCamVidData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('IdDevice',
					'DateCreatedFormat',
					'Humidity',
					'Temperature',
					'VoltageBattery',
					'VoltagePanel',
					'WindVelocity',
					'WindDirection',
					'RainCounter',
					'img_file_name',
					'Status',
					)
	list_filter = ('Status','IdDevice')
admin.site.register(CamVidData, confCamVidData)

## ==================== TrapViewData =====================
class TrapViewDataResource(resources.ModelResource):
    class Meta:
        model = TrapViewData

@admin.register(TrapViewData)
class TrapViewDataAdmin(ImportExportModelAdmin):
	resource_class = TrapViewDataResource

	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreate'
	DateCreatedFormat.short_description = 'Date Create'

	list_display = (
        'IdDevice',
		'DateCreatedFormat',
		'Humidity',
		'Temperature',
		'VoltageBattery',
		'img_bool',
		'Status',
    )
	search_fields = ('IdDevice',)
	list_filter = ('IdDevice',)

## ==================== Wheather station Data =====================
class WeatherStationDataResource(resources.ModelResource):
    class Meta:
        model = WeatherStationData
	
@admin.register(WeatherStationData)
class WeatherStationDataAdmin(ImportExportModelAdmin):
	resource_class = WeatherStationDataResource

	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreate'
	DateCreatedFormat.short_description = 'Date Create'

	list_display = (
        'IdDevice',
		'DateCreatedFormat',
		'Humidity',
		'Temperature',
		'VoltageBattery',
		'WindVelocity',
		'WindDirection',
		'RainCounter',
		'Radiation',
		'Status',
    )
	search_fields = ('IdDevice',)
	list_filter = ('IdDevice',)

## ==================== Gateway Data =====================
class confGatewayData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('IdDevice',
					'DateCreatedFormat',
					'VoltageBattery',
					'Status',
					)
	list_filter = ('Status','IdDevice')
admin.site.register(GatewayData, confGatewayData)