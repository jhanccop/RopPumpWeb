from django.db import models
from django.db.models import Max, Subquery, OuterRef


class WeatherStationManager(models.Manager):

    def get_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        )

    def list_by_company(self, company_name):
        return self.filter(
            Owner__CompanyId__CompanyName=company_name
        ).values(
            'id', 'StationName', 'Description',
            'Latitude', 'Longitude', 'Altitude',
            'Status',
            'HasTempHumidity',
            'HasSolarRadiation', 'HasPrecipitation', 'HasWind',
        )


class WeatherReadingManager(models.Manager):

    def get_by_station(self, station_id):
        return self.filter(Station__id=station_id).order_by('-DateCreate')

    def get_latest_by_station(self, station_id):
        return self.filter(Station__id=station_id).order_by('-DateCreate').first()

    def get_range_by_station(self, station_id, date_from, date_to):
        return self.filter(
            Station__id=station_id,
            DateCreate__date__gte=date_from,
            DateCreate__date__lte=date_to,
        ).order_by('-DateCreate')

    def get_range_by_company(self, company_name, date_from, date_to):
        return self.filter(
            Station__Owner__CompanyId__CompanyName=company_name,
            DateCreate__date__gte=date_from,
            DateCreate__date__lte=date_to,
        ).values(
            'id',
            'Station__StationName',
            'DateCreate',
            'Temperature', 'Humidity',
            'SolarRadiation', 'Precipitation',
            'WindSpeed', 'WindDirection',
        ).order_by('Station__StationName', 'DateCreate')

    def get_latest_per_station(self, company_name):
        """Returns the most recent reading for each station of a company."""
        from Apps.FAUNA.weatherStation.models import WeatherReading
        latest_ids = (
            self.filter(Station__Owner__CompanyId__CompanyName=company_name)
            .values('Station')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )
        return self.filter(id__in=latest_ids).select_related('Station').order_by('Station__StationName')
