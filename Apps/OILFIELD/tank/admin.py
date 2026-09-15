from django.contrib import admin
from django.utils.html import format_html

from .models import TankStation, TankIoTReading


class TankIoTReadingInline(admin.TabularInline):
    model   = TankIoTReading
    extra   = 0
    max_num = 20
    readonly_fields = ('DateCreate', 'LocalTimestamp', 'TypeConn',
                       'Level', 'Temperature', 'WaterLevel', 'Volume', 'VoltageBattery')
    fields  = readonly_fields
    can_delete = False
    show_change_link = False
    ordering = ('-DateCreate',)


@admin.register(TankStation)
class TankStationAdmin(admin.ModelAdmin):
    list_display  = ('Name', 'MacAddress', 'tank_code', 'SensorType',
                     'SamplingRate', 'Status', 'LastSeen', 'VoltageBattery')
    list_filter   = ('Status', 'SensorType')
    search_fields = ('Name', 'MacAddress', 'Tank__Code')
    readonly_fields = ('DateCreate', 'LastSeen', 'VoltageBattery')
    inlines = [TankIoTReadingInline]

    fieldsets = (
        ('Identificación', {
            'fields': ('Name', 'Description', 'MacAddress', 'Owner', 'DateCreate'),
        }),
        ('Tanque asociado', {
            'fields': ('Tank',),
        }),
        ('Configuración del sensor', {
            'fields': ('SensorType', 'SamplingRate'),
        }),
        ('Estado', {
            'fields': ('Status', 'LastSeen', 'VoltageBattery'),
        }),
        ('MQTT (override)', {
            'classes': ('collapse',),
            'fields': ('MqttBroker', 'MqttPort'),
        }),
    )

    @admin.display(description='Tanque', ordering='Tank__Code')
    def tank_code(self, obj):
        return obj.Tank.Code if obj.Tank else '—'


@admin.register(TankIoTReading)
class TankIoTReadingAdmin(admin.ModelAdmin):
    list_display  = ('Station', 'DateCreate', 'LocalTimestamp',
                     'Level', 'Temperature', 'WaterLevel', 'Volume', 'VoltageBattery', 'TypeConn')
    list_filter   = ('Station', 'TypeConn')
    search_fields = ('Station__Name', 'Station__MacAddress')
    readonly_fields = ('DateCreate',)
    date_hierarchy = 'DateCreate'
    ordering = ('-DateCreate',)
