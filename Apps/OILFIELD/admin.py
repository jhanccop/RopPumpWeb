from django.contrib import admin

from .models import (
    Battery,
    Manifold,
    Tank,
    TankCalibration,
    PumpingUnit,
    Well,
    WellDailyProduction,
    TankReading,
    PumpingReading,
    OperationalAlert,
    AlertRule,
    WellEvent,
)


@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    list_display  = ['Code', 'Name', 'Status']
    list_filter   = ['Status']
    search_fields = ['Code', 'Name']


@admin.register(Manifold)
class ManifoldAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'Battery', 'Status']
    list_filter   = ['Status']
    search_fields = ['Code', 'Name']


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display  = ['Code', 'Name', 'Battery', 'Type', 'NominalCapacity', 'Status']
    list_filter   = ['Type', 'Status', 'Battery']
    search_fields = ['Code', 'Name']


@admin.register(TankCalibration)
class TankCalibrationAdmin(admin.ModelAdmin):
    list_display  = ['Tank', 'Level', 'Volume']
    list_filter   = ['Tank']
    search_fields = ['Tank__Code']


@admin.register(PumpingUnit)
class PumpingUnitAdmin(admin.ModelAdmin):
    list_display  = ['Code', 'Name', 'Type', 'Status']
    list_filter   = ['Type', 'Status']
    search_fields = ['Code', 'Name']


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display   = ['Code', 'Name', 'Battery', 'LiftType', 'Status', 'ProductionTarget']
    list_filter    = ['Status', 'LiftType', 'Battery']
    search_fields  = ['Code', 'Name']
    raw_id_fields  = ['PumpingUnit']


@admin.register(WellDailyProduction)
class WellDailyProductionAdmin(admin.ModelAdmin):
    list_display   = ['Well', 'OperativeDate', 'OilProduction', 'WaterProduction', 'RunTime', 'Fillage', 'OperationalCondition']
    list_filter    = ['OperationalCondition', 'Well__Battery']
    date_hierarchy = 'OperativeDate'
    search_fields  = ['Well__Code']


@admin.register(TankReading)
class TankReadingAdmin(admin.ModelAdmin):
    list_display   = ['Tank', 'ReadingDate', 'Level', 'Volume', 'Source']
    list_filter    = ['Source', 'Tank']
    date_hierarchy = 'ReadingDate'
    search_fields  = ['Tank__Code']


@admin.register(PumpingReading)
class PumpingReadingAdmin(admin.ModelAdmin):
    list_display   = ['Well', 'DateCreate', 'SPM', 'Fillage', 'OilProduction', 'MotorCurrent', 'OperationalStatus']
    list_filter    = ['OperationalStatus']
    date_hierarchy = 'DateCreate'
    search_fields  = ['Well__Code']


@admin.register(OperationalAlert)
class OperationalAlertAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'Severity', 'Status', 'DateCreate']
    list_filter   = ['Severity', 'Status', 'AlertType']
    search_fields = ['Message', 'Variable']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'AssetType', 'Variable', 'Condition', 'Threshold', 'Severity', 'IsActive']
    list_filter   = ['AssetType', 'Severity', 'IsActive']
    search_fields = ['Description']


@admin.register(WellEvent)
class WellEventAdmin(admin.ModelAdmin):
    list_display  = ['Well', 'EventType', 'EventDate', 'DateCreate']
    list_filter   = ['EventType']
    search_fields = ['Well__Code', 'Description']
    date_hierarchy = 'EventDate'
