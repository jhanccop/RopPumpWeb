from datetime import datetime, time, timedelta, timezone as dt_utc
from zoneinfo import ZoneInfo

from django.db import models
from django.db.models import Max

_LIMA_TZ = ZoneInfo('America/Lima')


def lima_day_bounds(date_from, date_to):
    """Fechas Lima [date_from, date_to] → límites naive UTC [inicio, fin) (DateCreate se guarda en UTC)."""
    def to_utc(d):
        return datetime.combine(d, time.min, _LIMA_TZ).astimezone(dt_utc.utc).replace(tzinfo=None)
    return to_utc(date_from), to_utc(date_to + timedelta(days=1))


# Variables registradas por cada lectura (orden usado en reportes y CSV)
READING_FIELDS = (
    'Temperature', 'Humidity',
    'WindDirection', 'WindSpeed',
    'Precipitation', 'SolarRadiation',
    'RawDistance', 'WaterLevel', 'WaterPH', 'WaterTemperature',
)


class HydroStationManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )

    def list_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        ).values(
            'id', 'StationName', 'Description', 'MacAddress',
            'Latitude', 'Longitude', 'Altitude',
            'WaterBodyType', 'WaterBodyName',
            'LevelTare', 'LevelWarning', 'LevelCritical',
            'Status',
            'HasTempHumidity', 'HasSolarRadiation', 'HasPrecipitation', 'HasWind',
            'HasWaterLevel', 'HasWaterPH', 'HasWaterTemp',
        )


class HydroReadingManager(models.Manager):

    def get_by_station(self, station_id):
        return self.filter(Station__id=station_id).order_by('-DateCreate')

    def get_latest_by_station(self, station_id):
        return self.filter(Station__id=station_id).order_by('-DateCreate').first()

    def get_range_by_station(self, station_id, date_from, date_to):
        start, end = lima_day_bounds(date_from, date_to)
        return self.filter(
            Station__id=station_id,
            DateCreate__gte=start,
            DateCreate__lt=end,
        ).order_by('-DateCreate')

    def get_range_by_company(self, company_name, date_from, date_to):
        start, end = lima_day_bounds(date_from, date_to)
        return self.filter(
            Station__Owner__CompanyId__CompanyName=company_name,
            DateCreate__gte=start,
            DateCreate__lt=end,
        ).values(
            'id', 'Station__StationName', 'DateCreate', *READING_FIELDS,
        ).order_by('Station__StationName', 'DateCreate')

    def get_latest_per_station(self, company_name=None):
        """Última lectura de cada estación (de una compañía, o de todas las activas)."""
        qs = self.all()
        if company_name:
            qs = qs.filter(Station__Owner__CompanyId__CompanyName=company_name)
        else:
            qs = qs.filter(Station__Status='Active')
        latest_ids = (
            qs.values('Station')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )
        return self.filter(id__in=latest_ids).select_related('Station').order_by('Station__StationName')
