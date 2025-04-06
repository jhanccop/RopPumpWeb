from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
	RodPumpWell,
	Tank,
	Environmental,
	VisualSamplingPoint,
	InsectMonitoring) #, WellsTanks

"""class WellsTanksInLine(admin.TabularInline):
	model = WellsTanks
	extra = 1
	#autocomplete_fields = [WellsAssigned]
"""

## ==================== Rod Pump Equipment =====================
class RodPumpWellResource(resources.ModelResource):
    class Meta:
        model = RodPumpWell

@admin.register(RodPumpWell)
class RodPumpWellAdmin(ImportExportModelAdmin):
	resource_class = RodPumpWellResource

	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreate'
	DateCreatedFormat.short_description = 'Date Create'

	list_display = (
		'id',
        'WellName',
		'FieldName',
		'BatteryName',
		'GroupName',
		'SupervisorUser',
		'PumpIntake',
		'StrokeLength',
		'EngineType',
    )
	search_fields = ('FieldName','WellName')
	list_filter = ('FieldName',)

## ==================== Tank Equipment =====================
class TanklResource(resources.ModelResource):
    class Meta:
        model = Tank

@admin.register(Tank)
class TankAdmin(ImportExportModelAdmin):
	resource_class = TanklResource

	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreate'
	DateCreatedFormat.short_description = 'Date Create'

	list_display = (
		'id',
        'TankName',
		'FieldName',
		'BatteryName',
		'GroupName',
		'SupervisorUser',
		'TankHeight',
		'TankFactor',
		'Status'
    )
	search_fields = ('FieldName','TankName')
	list_filter = ('FieldName',)


class confEnvironmental(admin.ModelAdmin):
	#inlines = [WellsTanksInLine,]
	list_display = (
		'EnvironmentalName',
		'GroupName',
		'SupervisorUser',
		'Status'
	)
	def full_name(self, obj):
		return obj.EnvironmentalName
	
	list_filter = ('GroupName','SupervisorUser','Status')

class confVisualSamplingPoint(admin.ModelAdmin):
	#inlines = [WellsTanksInLine,]
	list_display = (
		'VisualSamplingPointName',
		'GroupName',
		'SupervisorUser',
		'Status'
	)
	def full_name(self, obj):
		return obj.VisualSamplingPointName
	
	list_filter = ('GroupName','SupervisorUser','Status')

class confInsectMonitoring(admin.ModelAdmin):
	#inlines = [WellsTanksInLine,]
	list_display = (
		'name',
		'GroupName',
		'SupervisorUser',
		'Status'
	)
	def full_name(self, obj):
		return obj.VisualSamplingPointName
	
	list_filter = ('GroupName','SupervisorUser','Status')

#admin.site.register(WellsTanks)
#admin.site.register(Tank, confTank)
admin.site.register(Environmental, confEnvironmental)
admin.site.register(VisualSamplingPoint, confVisualSamplingPoint)
admin.site.register(InsectMonitoring, confInsectMonitoring)