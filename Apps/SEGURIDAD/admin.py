from django.contrib import admin
from .models import SecurityDevice, Sensor, EventLog


class SensorInline(admin.TabularInline):
    model  = Sensor
    extra  = 0
    fields = ['SensorIndex', 'SensorKey', 'Name', 'Enabled', 'Category', 'CurrentState']
    readonly_fields = ['CurrentState']


@admin.register(SecurityDevice)
class SecurityDeviceAdmin(admin.ModelAdmin):
    list_display  = ['Name', 'MacAddress', 'Location', 'Status', 'LastSeen']
    list_filter   = ['Status']
    search_fields = ['Name', 'MacAddress', 'Location']
    inlines       = [SensorInline]
    readonly_fields = ['LastSeen', 'BuzzerState', 'BypassState',
                       'Temperature', 'Humidity', 'WifiOK', 'MqttOK']


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display  = ['ServerTimestamp', 'Device', 'Origin', 'SensorName',
                     'Estado', 'Category']
    list_filter   = ['Device', 'Category', 'Estado', 'Origin']
    search_fields = ['SensorName', 'Device__Name']
    readonly_fields = ['ServerTimestamp']
    date_hierarchy = 'ServerTimestamp'
