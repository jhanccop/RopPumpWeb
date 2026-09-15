from django.contrib import admin
from .models import WellAnalyzerStation, AnalyzerReading


class AnalyzerReadingInline(admin.TabularInline):
    model   = AnalyzerReading
    extra   = 0
    max_num = 20
    readonly_fields = ('DateCreate', 'LocalTimestamp', 'TypeConn',
                       'SPM', 'Fillage', 'RunTime', 'OilProduction', 'WaterProduction',
                       'Torque', 'MotorCurrent', 'Temperature', 'DynamicLevel',
                       'OperationalStatus', 'VoltageBattery')
    fields  = readonly_fields
    can_delete = False
    ordering = ('-DateCreate',)


@admin.register(WellAnalyzerStation)
class WellAnalyzerStationAdmin(admin.ModelAdmin):
    list_display  = ('Name', 'MacAddress', 'well_code', 'SamplingRate',
                     'Status', 'OperationalStatus', 'LastSeen', 'VoltageBattery')
    list_filter   = ('Status', 'OperationalStatus')
    search_fields = ('Name', 'MacAddress', 'Well__Code')
    readonly_fields = ('DateCreate', 'LastSeen', 'VoltageBattery', 'OperationalStatus')
    inlines = [AnalyzerReadingInline]

    fieldsets = (
        ('Identificación', {
            'fields': ('Name', 'Description', 'MacAddress', 'Owner', 'DateCreate'),
        }),
        ('Pozo asociado', {
            'fields': ('Well',),
        }),
        ('Configuración', {
            'fields': ('SamplingRate',),
        }),
        ('Estado en tiempo real', {
            'fields': ('Status', 'OperationalStatus', 'LastSeen', 'VoltageBattery'),
        }),
        ('MQTT (override)', {
            'classes': ('collapse',),
            'fields': ('MqttBroker', 'MqttPort'),
        }),
    )

    @admin.display(description='Pozo', ordering='Well__Code')
    def well_code(self, obj):
        return obj.Well.Code if obj.Well else '—'


@admin.register(AnalyzerReading)
class AnalyzerReadingAdmin(admin.ModelAdmin):
    list_display  = ('Station', 'DateCreate', 'SPM', 'Fillage', 'RunTime',
                     'OilProduction', 'WaterProduction', 'OperationalStatus', 'TypeConn')
    list_filter   = ('Station', 'OperationalStatus', 'TypeConn')
    search_fields = ('Station__Name', 'Station__MacAddress')
    readonly_fields = ('DateCreate',)
    date_hierarchy = 'DateCreate'
    ordering = ('-DateCreate',)
