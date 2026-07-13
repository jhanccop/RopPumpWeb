from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import WeatherStation, WeatherReading


# =================== Weather Station =====================
class WeatherStationResource(resources.ModelResource):
    class Meta:
        model = WeatherStation


@admin.register(WeatherStation)
class WeatherStationAdmin(ImportExportModelAdmin):
    resource_class = WeatherStationResource

    def DateCreatedFormat(self, obj):
        from django.utils.timezone import localtime; return localtime(obj.DateCreate).strftime("%Y-%m-%d %H:%M:%S")
    DateCreatedFormat.admin_order_field = 'DateCreate'
    DateCreatedFormat.short_description = 'Date Create'

    list_display = (
        'id',
        'StationName',
        'Latitude',
        'Longitude',
        'Altitude',
        'HasTempHumidity',
        'HasSolarRadiation',
        'HasPrecipitation',
        'HasWind',
        'Status',
        'DateCreatedFormat',
    )
    search_fields = ('StationName', 'Description')
    list_filter = ('Status', 'HasTempHumidity', 'HasSolarRadiation')


# =================== Weather Reading =====================
class WeatherReadingResource(resources.ModelResource):
    class Meta:
        model = WeatherReading


@admin.register(WeatherReading)
class WeatherReadingAdmin(ImportExportModelAdmin):
    resource_class = WeatherReadingResource

    list_display = (
        'id',
        'Station',
        'DateCreate',
        'Temperature',
        'Humidity',
        'SolarRadiation',
        'Precipitation',
        'WindSpeed',
        'WindDirection',
        'VoltageBattery',
    )
    search_fields = ('Station__StationName',)
    list_filter = ('Station', 'DateCreate')
    date_hierarchy = 'DateCreate'
