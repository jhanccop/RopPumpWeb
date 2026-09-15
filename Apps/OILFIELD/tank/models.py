"""
OILFIELD – Tank sub-app models
================================
  TankStation    → dispositivo IoT (identificado por MAC address)
  TankIoTReading → serie temporal unificada: IoT vía MQTT + entradas manuales

  Source = 'iot'    → datos del dispositivo (Station obligatorio)
  Source = 'manual' → lectura ingresada por operador (Station puede ser nulo
                       si el tanque no tiene dispositivo IoT)
  Source = 'scada'  → integración SCADA futura

Infrastructure models (Battery, Tank, Well, …) live in Apps.OILFIELD.models.
"""
from django.conf import settings
from django.db import models


# ── Choices reutilizables ─────────────────────────────────────────────────────

CONN_CHOICES = (
    ('WIFI',  'WiFi'),
    ('LTE',   'LTE/4G'),
    ('GPRS',  'GPRS'),
    ('RS485', 'RS-485'),
)

SAMPLING_CHOICES = (
    (900,  '15 min'),
    (1800, '30 min'),
    (3600, '1 hora'),
    (7200, '2 horas'),
)

SENSOR_TYPE_CHOICES = (
    ('ultrasonic', 'Ultrasónico'),
    ('radar',      'Radar'),
    ('pressure',   'Presión diferencial'),
    ('float',      'Flotador'),
    ('manual',     'Manual'),
)

STATUS_CHOICES = (
    ('active',      'Activo'),
    ('inactive',    'Inactivo'),
    ('maintenance', 'Mantenimiento'),
    ('fault',       'Falla'),
)


# ── TankStation  (dispositivo de medición) ────────────────────────────────────

class TankStation(models.Model):
    """
    Dispositivo IoT que monitorea un tanque.
    Identificado por MAC address — análogo a WeatherStation en FAUNA.
    """
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tank_stations',
    )
    DateCreate = models.DateTimeField(auto_now_add=True)

    # ── Identificación ────────────────────────────────────────────────────────
    Name        = models.CharField('Nombre', max_length=100, unique=True)
    Description = models.TextField('Descripción', max_length=500, blank=True, null=True)
    MacAddress  = models.CharField(
        'MAC Address', max_length=17, unique=True,
        help_text='Identificador del dispositivo, ej. AA:BB:CC:DD:EE:FF',
    )

    # ── Tanque asociado ───────────────────────────────────────────────────────
    # FK a Apps.OILFIELD.models.Tank (infraestructura)
    Tank = models.ForeignKey(
        'OILFIELD.Tank',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='iot_stations',
        verbose_name='Tanque monitorado',
        help_text='Tanque de la infraestructura al que está instalado este sensor.',
    )

    # ── Configuración del sensor ──────────────────────────────────────────────
    SensorType  = models.CharField('Tipo de sensor', max_length=20,
                                    choices=SENSOR_TYPE_CHOICES, default='ultrasonic')
    SamplingRate = models.IntegerField('Intervalo de muestreo (s)',
                                        choices=SAMPLING_CHOICES, default=1800)

    # ── Estado en tiempo real ─────────────────────────────────────────────────
    Status         = models.CharField('Estado', max_length=20,
                                       choices=STATUS_CHOICES, default='active')
    LastSeen       = models.DateTimeField('Última conexión', null=True, blank=True)
    VoltageBattery = models.FloatField('Voltaje batería (V)', null=True, blank=True)

    # ── MQTT (opcional: override global del broker) ───────────────────────────
    MqttBroker = models.CharField('Broker MQTT', max_length=200, blank=True, null=True)
    MqttPort   = models.PositiveIntegerField('Puerto MQTT', default=1883)

    class Meta:
        ordering = ['Name']
        verbose_name = 'Estación de Tanque'
        verbose_name_plural = 'Estaciones de Tanque'

    def __str__(self):
        tank_code = self.Tank.Code if self.Tank else '—'
        return f'{self.Name} [{tank_code}] ({self.MacAddress})'


# ── TankIoTReading  (serie temporal de telemetría) ────────────────────────────

class TankIoTReading(models.Model):
    """
    Lectura unificada de tanque.

    Source='iot'    → MQTT desde dispositivo (Station requerida)
    Source='manual' → ingreso manual por operador (Station opcional)
    Source='scada'  → integración SCADA futura
    """
    id = models.BigAutoField(primary_key=True)

    # ── Fuente ────────────────────────────────────────────────────────────────
    SOURCE_CHOICES = (
        ('iot',    'IoT'),
        ('manual', 'Manual'),
        ('scada',  'SCADA'),
    )
    Source = models.CharField('Fuente', max_length=10,
                               choices=SOURCE_CHOICES, default='iot')

    # ── Dispositivo (nullable para entradas manuales sin estación) ────────────
    Station = models.ForeignKey(
        TankStation,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='readings',
    )
    # FK directa al tanque — requerida (se puede derivar de Station.Tank para IoT)
    Tank = models.ForeignKey(
        'OILFIELD.Tank',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='iot_readings',
        verbose_name='Tanque',
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    DateCreate     = models.DateTimeField('Timestamp servidor', auto_now_add=True)
    ReadingDate    = models.DateTimeField('Fecha/hora lectura', null=True, blank=True)   # = server_dt para IoT, ingresado para manual
    LocalTimestamp = models.DateTimeField('Timestamp dispositivo', null=True, blank=True)
    TypeConn       = models.CharField('Conexión', max_length=10,
                                       choices=CONN_CHOICES, null=True, blank=True)

    # ── Variables de proceso ──────────────────────────────────────────────────
    Level       = models.FloatField('Nivel (cm)',       null=True, blank=True)
    Temperature = models.FloatField('Temperatura (°C)', null=True, blank=True)
    WaterLevel  = models.FloatField('Nivel agua (cm)',  null=True, blank=True)
    Volume      = models.FloatField('Volumen (bbl)',    null=True, blank=True)

    # ── Estado del dispositivo ────────────────────────────────────────────────
    VoltageBattery = models.FloatField('Batería (V)', null=True, blank=True)

    # ── Campos manuales ───────────────────────────────────────────────────────
    Notes = models.CharField('Notas', max_length=200, blank=True)
    EnteredBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tank_iot_readings_entered',
    )

    class Meta:
        ordering = ['-ReadingDate']
        verbose_name = 'Lectura de Tanque'
        verbose_name_plural = 'Lecturas de Tanque'
        indexes = [
            models.Index(fields=['Station', 'ReadingDate']),
            models.Index(fields=['Tank',    'ReadingDate']),
        ]

    def __str__(self):
        tank_code = (self.Tank.Code if self.Tank
                     else (self.Station.Tank.Code if self.Station and self.Station.Tank else '?'))
        return f'{tank_code} [{self.get_Source_display()}] {self.ReadingDate:%Y-%m-%d %H:%M}'

    @property
    def effective_tank(self):
        """Retorna el Tank asociado, ya sea directo o a través de la estación."""
        return self.Tank or (self.Station.Tank if self.Station else None)

    @property
    def LevelPercent(self):
        """
        Nivel en % respecto a la altura del tanque.
        Tank.Height se almacena en metros, Level en mm.
        → LevelPercent = Level(mm) / (Height(m) * 1000) * 100
        """
        try:
            h = self.effective_tank.Height
            if h and self.Level is not None:
                pct = round(self.Level / (h * 1000) * 100, 1)
                return min(pct, 100.0)   # nunca > 100%
        except (AttributeError, TypeError, ZeroDivisionError):
            pass
        return None

    @property
    def Level_cm(self):
        """Convierte Level (mm) a centímetros."""
        if self.Level is not None:
            return round(self.Level / 10, 1)
        return None
