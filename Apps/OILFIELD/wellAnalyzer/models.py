"""
OILFIELD – WellAnalyzer sub-app models
========================================
Mirrors the FAUNA/camera pattern:
  WellAnalyzerStation → dispositivo dinamométrico (MAC address)
  AnalyzerReading     → serie temporal de telemetría (SPM, Fillage, etc.)
"""
from django.conf import settings
from django.db import models


CONN_CHOICES = (
    ('WIFI',  'WiFi'),
    ('LTE',   'LTE/4G'),
    ('GPRS',  'GPRS'),
    ('RS485', 'RS-485'),
)

SAMPLING_CHOICES = (
    (300,  '5 min'),
    (900,  '15 min'),
    (1800, '30 min'),
    (3600, '1 hora'),
)

STATUS_CHOICES = (
    ('active',      'Activo'),
    ('inactive',    'Inactivo'),
    ('maintenance', 'Mantenimiento'),
    ('fault',       'Falla'),
)

OPERATIONAL_STATUS_CHOICES = (
    ('producing',   'Produciendo'),
    ('pump_off',    'Pump Off'),
    ('gas_lock',    'Gas Lock'),
    ('fluid_pound', 'Fluid Pound'),
    ('low_fillage', 'Bajo Llenado'),
    ('overloaded',  'Sobrecarga'),
    ('maintenance', 'Mantenimiento'),
    ('stopped',     'Detenido'),
    ('fault_mech',  'Falla Mecánica'),
    ('inactive',    'Inactivo'),
)


# ── WellAnalyzerStation  (dispositivo) ───────────────────────────────────────

class WellAnalyzerStation(models.Model):
    """
    Dispositivo dinamométrico IoT instalado en un pozo.
    Identificado por MAC address — análogo a WeatherStation en FAUNA.
    """
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='well_analyzer_stations',
    )
    DateCreate = models.DateTimeField(auto_now_add=True)

    # ── Identificación ────────────────────────────────────────────────────────
    Name        = models.CharField('Nombre', max_length=100, unique=True)
    Description = models.TextField('Descripción', max_length=500, blank=True, null=True)
    MacAddress  = models.CharField(
        'MAC Address', max_length=17, unique=True,
        help_text='Identificador del dispositivo, ej. AA:BB:CC:DD:EE:FF',
    )

    # ── Pozo asociado ─────────────────────────────────────────────────────────
    Well = models.ForeignKey(
        'OILFIELD.Well',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='analyzer_stations',
        verbose_name='Pozo monitorado',
    )

    # ── Configuración ─────────────────────────────────────────────────────────
    SamplingRate = models.IntegerField('Intervalo de muestreo (s)',
                                        choices=SAMPLING_CHOICES, default=1800)

    # ── Estado en tiempo real ─────────────────────────────────────────────────
    Status             = models.CharField('Estado', max_length=20,
                                           choices=STATUS_CHOICES, default='active')
    OperationalStatus  = models.CharField('Estado operacional', max_length=20,
                                           choices=OPERATIONAL_STATUS_CHOICES,
                                           default='inactive', blank=True)
    LastSeen           = models.DateTimeField('Última conexión', null=True, blank=True)
    VoltageBattery     = models.FloatField('Voltaje batería (V)', null=True, blank=True)

    # ── MQTT (opcional: override) ─────────────────────────────────────────────
    MqttBroker = models.CharField('Broker MQTT', max_length=200, blank=True, null=True)
    MqttPort   = models.PositiveIntegerField('Puerto MQTT', default=1883)

    class Meta:
        ordering = ['Name']
        verbose_name = 'Analizador de Pozo'
        verbose_name_plural = 'Analizadores de Pozo'

    def __str__(self):
        well_code = self.Well.Code if self.Well else '—'
        return f'{self.Name} [{well_code}] ({self.MacAddress})'


# ── AnalyzerReading  (serie temporal dinamométrica) ───────────────────────────

class AnalyzerReading(models.Model):
    """
    Lectura dinamométrica recibida del dispositivo vía MQTT.
    Análogo a WeatherReading en FAUNA.
    """
    id = models.BigAutoField(primary_key=True)

    Station = models.ForeignKey(
        WellAnalyzerStation,
        on_delete=models.CASCADE,
        related_name='readings',
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    DateCreate     = models.DateTimeField('Timestamp servidor')
    LocalTimestamp = models.DateTimeField('Timestamp dispositivo', null=True, blank=True)
    TypeConn       = models.CharField('Conexión', max_length=10,
                                       choices=CONN_CHOICES, null=True, blank=True)

    # ── Variables de proceso ──────────────────────────────────────────────────
    SPM                  = models.FloatField('SPM',                    null=True, blank=True)
    Fillage              = models.FloatField('Fillage (%)',             null=True, blank=True)
    RunTime              = models.FloatField('Run Time (h)',            null=True, blank=True)
    OilProduction        = models.FloatField('Prod. Petróleo (bbl/d)', null=True, blank=True)
    WaterProduction      = models.FloatField('Prod. Agua (bbl/d)',     null=True, blank=True)
    Torque               = models.FloatField('Torque (ft-lb)',         null=True, blank=True)
    MotorCurrent         = models.FloatField('Corriente (A)',          null=True, blank=True)
    Vibration            = models.FloatField('Vibración (mm/s)',       null=True, blank=True)
    Temperature          = models.FloatField('Temperatura (°C)',       null=True, blank=True)
    DynamicLevel         = models.FloatField('Nivel dinámico (m)',     null=True, blank=True)
    VolumetricEfficiency = models.FloatField('Efic. volumétrica (%)',  null=True, blank=True)

    # ── Estado operacional ────────────────────────────────────────────────────
    OperationalStatus = models.CharField('Estado operacional', max_length=20,
                                          choices=OPERATIONAL_STATUS_CHOICES,
                                          default='producing', blank=True)

    # ── Estado del dispositivo ────────────────────────────────────────────────
    VoltageBattery = models.FloatField('Batería (V)', null=True, blank=True)

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Lectura Dinamométrica'
        verbose_name_plural = 'Lecturas Dinamométricas'
        indexes = [
            models.Index(fields=['Station', 'DateCreate']),
        ]

    def __str__(self):
        return f'{self.Station.Name} {self.DateCreate:%Y-%m-%d %H:%M}'

    @property
    def WaterCut(self):
        total = (self.OilProduction or 0) + (self.WaterProduction or 0)
        if self.WaterProduction and total:
            return round(self.WaterProduction / total * 100, 1)
        return None
