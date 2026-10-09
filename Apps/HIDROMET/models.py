from django.db import models
from django.conf import settings

from .managers import HydroStationManager, HydroReadingManager


class HydroStation(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='hm_owner'
    )
    DateCreate = models.DateTimeField(auto_now_add=True)

    StationName = models.CharField('Nombre de estación', max_length=100, unique=True)
    Description = models.TextField('Descripción', max_length=500, blank=True, null=True)

    # Location
    Latitude = models.FloatField('Latitud', null=True, blank=True)
    Longitude = models.FloatField('Longitud', null=True, blank=True)
    Altitude = models.FloatField('Altitud (m.s.n.m.)', null=True, blank=True)

    # Monitored water body
    WATERBODY_CHOICES = (
        ('Rio',      'Río'),
        ('Cuenca',   'Cuenca'),
        ('Quebrada', 'Quebrada'),
        ('Laguna',   'Laguna / Lago'),
        ('Canal',    'Canal'),
        ('Otro',     'Otro'),
    )
    WaterBodyType = models.CharField('Tipo de cuerpo de agua', max_length=10,
                                     choices=WATERBODY_CHOICES, default='Rio')
    WaterBodyName = models.CharField('Nombre del cuerpo de agua', max_length=100,
                                     blank=True, null=True)

    # Water level reference: el sensor mide la distancia desde arriba hasta la superficie del agua
    LevelTare = models.FloatField(
        'Tara de altura (m)', null=True, blank=True,
        help_text='Distancia del sensor al fondo del cauce. Altura del flujo = tara − distancia medida.'
    )

    # Water level thresholds (m)
    LevelWarning = models.FloatField('Nivel de alerta (m)', null=True, blank=True)
    LevelCritical = models.FloatField('Nivel crítico (m)', null=True, blank=True)

    # Available sensors
    HasTempHumidity = models.BooleanField('Sensor Temperatura y Humedad', default=True)
    HasSolarRadiation = models.BooleanField('Sensor Radiación Solar', default=False)
    HasPrecipitation = models.BooleanField('Sensor Precipitación', default=False)
    HasWind = models.BooleanField('Sensor Viento', default=False)
    HasWaterLevel = models.BooleanField('Sensor Nivel de Agua', default=True)
    HasWaterPH = models.BooleanField('Sensor pH de Agua', default=False)
    HasWaterTemp = models.BooleanField('Sensor Temperatura de Agua', default=False)

    MacAddress = models.CharField('MAC Address', max_length=17, blank=True, null=True,
                                  help_text='e.g. AA:BB:CC:DD:EE:FF')

    SLEEP_CHOICES = (
        ('5m',  'Cada 5 minutos'),
        ('15m', 'Cada 15 minutos'),
        ('30m', 'Cada 30 minutos'),
        ('1h',  'Cada 1 hora'),
    )
    TimeSleep = models.CharField('Intervalo de lectura', max_length=3,
                                 choices=SLEEP_CHOICES, default='15m')

    STATUS_CHOICES = (
        ('Active', 'Activa'),
        ('Inactive', 'Inactiva'),
        ('Maintenance', 'Mantenimiento'),
        ('Out of service', 'Fuera de servicio'),
    )
    Status = models.CharField('Estado', max_length=50, choices=STATUS_CHOICES, default='Active')

    objects = HydroStationManager()

    class Meta:
        verbose_name = 'Estación Hidrometeorológica'
        verbose_name_plural = 'Estaciones Hidrometeorológicas'

    def __str__(self):
        return self.StationName

    def flow_height(self, raw_distance):
        """Altura del flujo a partir de la distancia medida por el sensor (desde arriba)."""
        if raw_distance is None or self.LevelTare is None:
            return None
        return round(self.LevelTare - raw_distance, 4)

    def level_state(self, level):
        """Clasifica un nivel de agua frente a los umbrales: normal | warning | critical."""
        if level is None:
            return None
        if self.LevelCritical is not None and level >= self.LevelCritical:
            return 'critical'
        if self.LevelWarning is not None and level >= self.LevelWarning:
            return 'warning'
        return 'normal'


class HydroReading(models.Model):
    id = models.BigAutoField(primary_key=True)

    Station = models.ForeignKey(
        HydroStation,
        on_delete=models.CASCADE,
        related_name='readings'
    )
    DateCreate      = models.DateTimeField('Fecha servidor', auto_now_add=False, auto_now=False)
    LocalTimestamp  = models.DateTimeField('Fecha dispositivo', null=True, blank=True)
    TypeConn        = models.CharField('Tipo de conexión', max_length=10, null=True, blank=True)

    # Meteorological variables
    Temperature = models.FloatField('Temperatura ambiente (°C)', null=True, blank=True)
    Humidity = models.FloatField('Humedad (%)', null=True, blank=True)
    WindDirection = models.FloatField('Dirección del viento (°)', null=True, blank=True)
    WindSpeed = models.FloatField('Velocidad del viento (m/s)', null=True, blank=True)
    Precipitation = models.FloatField('Precipitación (mm)', null=True, blank=True)
    SolarRadiation = models.FloatField('Radiación solar (W/m²)', null=True, blank=True)

    # Hydrological variables
    RawDistance = models.FloatField('Distancia medida (m)', null=True, blank=True,
                                    help_text='Lectura del sensor: distancia desde arriba hasta la superficie del agua.')
    WaterLevel = models.FloatField('Altura del flujo (m)', null=True, blank=True)
    WaterPH = models.FloatField('pH del agua', null=True, blank=True)
    WaterTemperature = models.FloatField('Temperatura del agua (°C)', null=True, blank=True)

    VoltageBattery = models.FloatField('Voltaje batería (V)', null=True, blank=True)

    objects = HydroReadingManager()

    class Meta:
        verbose_name = 'Lectura Hidrometeorológica'
        verbose_name_plural = 'Lecturas Hidrometeorológicas'
        ordering = ['-DateCreate']

    def __str__(self):
        return f'{self.Station} - {self.DateCreate}'

    def save(self, *args, **kwargs):
        # La altura del flujo se deriva de la distancia medida y la tara vigente de la estación
        if self.RawDistance is not None and self.Station.LevelTare is not None:
            self.WaterLevel = self.Station.flow_height(self.RawDistance)
        super().save(*args, **kwargs)

    @property
    def level_state(self):
        return self.Station.level_state(self.WaterLevel)
