from datetime import timezone as dt_utc
from zoneinfo import ZoneInfo

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import HydroStation, HydroReading

_LIMA_TZ = ZoneInfo('America/Lima')

def _fmt_lima(dt):
    """Formatea datetime naive (asumido UTC) o aware a hora Lima."""
    if dt is None:
        return '—'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_utc.utc)
    return dt.astimezone(_LIMA_TZ).strftime('%Y-%m-%d %H:%M')


# =================== Hydro Station =====================
class HydroStationResource(resources.ModelResource):
    class Meta:
        model = HydroStation


@admin.register(HydroStation)
class HydroStationAdmin(ImportExportModelAdmin):
    resource_class = HydroStationResource

    def DateCreatedFormat(self, obj):
        return _fmt_lima(obj.DateCreate)
    DateCreatedFormat.admin_order_field = 'DateCreate'
    DateCreatedFormat.short_description = 'Date Create'

    list_display = (
        'id',
        'StationName',
        'Owner',
        'WaterBodyType',
        'WaterBodyName',
        'MacAddress',
        'LevelTare',
        'Latitude',
        'Longitude',
        'Altitude',
        'LevelWarning',
        'LevelCritical',
        'Status',
        'DateCreatedFormat',
    )
    search_fields = ('StationName', 'Description', 'WaterBodyName', 'MacAddress')
    list_filter = ('Status', 'WaterBodyType', 'HasWaterLevel', 'HasWaterPH', 'HasWaterTemp')
    fieldsets = (
        ('General', {'fields': ('Owner', 'StationName', 'Description', 'Status')}),
        ('Ubicación', {'fields': ('Latitude', 'Longitude', 'Altitude',
                                  'WaterBodyType', 'WaterBodyName')}),
        ('Tara y umbrales de nivel', {
            'fields': ('LevelTare', 'LevelWarning', 'LevelCritical'),
            'description': 'Altura del flujo = tara − distancia medida por el sensor (montado arriba).',
        }),
        ('Dispositivo', {'fields': ('MacAddress', 'TimeSleep')}),
        ('Sensores', {'fields': ('HasTempHumidity', 'HasSolarRadiation', 'HasPrecipitation',
                                 'HasWind', 'HasWaterLevel', 'HasWaterPH', 'HasWaterTemp')}),
    )


# =================== Hydro Reading =====================
class HydroReadingResource(resources.ModelResource):
    class Meta:
        model = HydroReading


@admin.register(HydroReading)
class HydroReadingAdmin(ImportExportModelAdmin):
    resource_class = HydroReadingResource

    list_display = (
        'id',
        'Station',
        'DateCreate',
        'LocalTimestamp',
        'Temperature',
        'Humidity',
        'WindDirection',
        'WindSpeed',
        'Precipitation',
        'SolarRadiation',
        'RawDistance',
        'WaterLevel',
        'WaterPH',
        'WaterTemperature',
        'VoltageBattery',
    )
    search_fields = ('Station__StationName',)
    list_filter = ('Station', 'DateCreate')
    date_hierarchy = 'DateCreate'
    list_select_related = ('Station',)
