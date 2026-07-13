from django.contrib import admin

from .models import Substation, Transformer, ElectricalReading, AlertRule, Alert


# ---------------------------------------------------------------------------
# AlertRule inline (used inside TransformerAdmin)
# ---------------------------------------------------------------------------

class AlertRuleInline(admin.TabularInline):
    model = AlertRule
    fields = ('Variable', 'Condition', 'Threshold', 'Severity', 'IsActive', 'Description')
    extra = 1
    min_num = 0


# ---------------------------------------------------------------------------
# Substation
# ---------------------------------------------------------------------------

@admin.register(Substation)
class SubstationAdmin(admin.ModelAdmin):
    list_display = ('id', 'Name', 'Type', 'Status', 'NominalVoltage', 'InstalledCapacity', 'DateCreate')
    list_filter  = ('Type', 'Status')
    search_fields = ('Name', 'Description', 'Address')
    ordering = ('Name',)


# ---------------------------------------------------------------------------
# Transformer
# ---------------------------------------------------------------------------

@admin.register(Transformer)
class TransformerAdmin(admin.ModelAdmin):
    inlines = [AlertRuleInline]

    def DateCreateFormat(self, obj):
        return obj.DateCreate.strftime('%Y-%m-%d %H:%M:%S')
    DateCreateFormat.admin_order_field = 'DateCreate'
    DateCreateFormat.short_description = 'Date Create'

    list_display = (
        'id',
        'Code',
        'StationName',
        'Type',
        'Status',
        'NominalPower',
        'Substation',
        'DateCreateFormat',
    )
    list_filter  = ('Type', 'Status', 'CoolingType', 'Substation')
    search_fields = ('Code', 'Series', 'StationName', 'Manufacturer', 'Address')
    raw_id_fields = ('Owner', 'Substation')


# ---------------------------------------------------------------------------
# ElectricalReading
# ---------------------------------------------------------------------------

@admin.register(ElectricalReading)
class ElectricalReadingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'Transformer',
        'DateCreate',
        'HotSpotTemperature',
        'OilTemperature',
        'InternalPressure',
        'OilLevel',
        'Vibration',
        'OilHumidity',
    )
    list_filter  = ('Transformer',)
    search_fields = ('Transformer__Code', 'Transformer__StationName')
    date_hierarchy = 'DateCreate'
    readonly_fields = ('DateCreate',)


# ---------------------------------------------------------------------------
# AlertRule
# ---------------------------------------------------------------------------

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'Transformer', 'Variable', 'Condition', 'Threshold', 'Severity', 'IsActive')
    list_filter  = ('Severity', 'IsActive', 'Variable')
    search_fields = ('Transformer__Code', 'Transformer__StationName', 'Description')


# ---------------------------------------------------------------------------
# Alert
# ---------------------------------------------------------------------------

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'Transformer',
        'Variable',
        'Severity',
        'DetectedValue',
        'ThresholdValue',
        'Status',
        'DateCreate',
    )
    list_filter  = ('Severity', 'Status', 'Variable')
    search_fields = ('Transformer__Code', 'Transformer__StationName', 'Message', 'Variable')
    date_hierarchy = 'DateCreate'
    readonly_fields = ('DateCreate', 'DateAcknowledged', 'DateClosed')
