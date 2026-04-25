from django.db import models
from django.conf import settings

from .managers import WeatherStationManager, WeatherReadingManager


class WeatherStation(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='ws_owner'
    )
    DateCreate = models.DateTimeField(auto_now_add=True)

    StationName = models.CharField('Station Name', max_length=100, unique=True)
    Description = models.TextField('Description', max_length=500, blank=True, null=True)

    # Location
    Latitude = models.FloatField('Latitude', null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)
    Altitude = models.FloatField('Altitude (m)', null=True, blank=True)

    # Available sensors
    HasTempHumidity = models.BooleanField('Temperature & Humidity Sensor', default=True)
    HasSolarRadiation = models.BooleanField('Solar Radiation Sensor', default=False)
    HasPrecipitation = models.BooleanField('Precipitation Sensor', default=False)
    HasWind = models.BooleanField('Wind Sensor', default=False)

    MacAddress = models.CharField('MAC Address', max_length=17, blank=True, null=True,
                                   help_text='e.g. AA:BB:CC:DD:EE:FF')

    SLEEP_CHOICES = (
        ('5m',  'Every 5 minutes'),
        ('30m', 'Every 30 minutes'),
        ('1h',  'Every 1 hour'),
    )
    TimeSleep = models.CharField('Reading Interval', max_length=3,
                                  choices=SLEEP_CHOICES, default='30m')

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Maintenance', 'Maintenance'),
        ('Out of service', 'Out of service'),
    )
    Status = models.CharField('Status', max_length=50, choices=STATUS_CHOICES, default='Active')

    objects = WeatherStationManager()

    class Meta:
        verbose_name = 'Weather Station'
        verbose_name_plural = 'Weather Stations'

    def __str__(self):
        return self.StationName


class WeatherReading(models.Model):
    id = models.BigAutoField(primary_key=True)

    Station = models.ForeignKey(
        WeatherStation,
        on_delete=models.CASCADE,
        related_name='readings'
    )
    DateCreate = models.DateTimeField('Date / Time', auto_now_add=False, auto_now=False)

    Temperature = models.FloatField('Temperature (°C)', null=True, blank=True)
    Humidity = models.FloatField('Humidity (%)', null=True, blank=True)
    SolarRadiation = models.FloatField('Solar Radiation (W/m²)', null=True, blank=True)
    Precipitation = models.FloatField('Precipitation (mm)', null=True, blank=True)
    WindSpeed = models.FloatField('Wind Speed (m/s)', null=True, blank=True)
    WindDirection = models.FloatField('Wind Direction (°)', null=True, blank=True)
    VoltageBattery = models.FloatField('Battery Voltage (V)', null=True, blank=True)

    objects = WeatherReadingManager()

    class Meta:
        verbose_name = 'Weather Reading'
        verbose_name_plural = 'Weather Readings'
        ordering = ['-DateCreate']

    def __str__(self):
        return f'{self.Station} - {self.DateCreate}'
