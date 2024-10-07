from django.contrib import admin

from .models import RodPumpData, TankData, EnvironmentalData, CamVidData

class confRPData(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('IdDevice','DateCreatedFormat','PumpFillage', 'Diagnosis','Recomendation')
	list_filter = ('Diagnosis','IdDevice')
admin.site.register(RodPumpData, confRPData)

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