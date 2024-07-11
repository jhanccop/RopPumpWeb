from django.contrib import admin

from .models import RodPumpWell, Tank, Environmental #, WellsTanks

"""class WellsTanksInLine(admin.TabularInline):
	model = WellsTanks
	extra = 1
	#autocomplete_fields = [WellsAssigned]
"""

class confRodPumpWell(admin.ModelAdmin):
	list_display = ('WellName','FieldName','BatteryName', 'GroupName','SupervisorUser','PumpIntake','StrokeLength','EngineType','Status')
	list_filter = ('FieldName','BatteryName','GroupName','SupervisorUser','Status',)
	search_fields = ['WellName']
admin.site.register(RodPumpWell, confRodPumpWell)

class confTank(admin.ModelAdmin):
	#inlines = [WellsTanksInLine,]
	list_display = (
		'TankName',
		'FieldName',
		'BatteryName',
		'GroupName',
		'SupervisorUser',
		'TankHeight',
		'TankFactor',
		'Status'
	)
	autocomplete_fields = ['WellsAssigned']
	def full_name(self, obj):
		return obj.TankName
	
	list_filter = ('FieldName','BatteryName','GroupName','SupervisorUser','Status')

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

#admin.site.register(WellsTanks)
admin.site.register(Tank, confTank)
admin.site.register(Environmental, confEnvironmental)
