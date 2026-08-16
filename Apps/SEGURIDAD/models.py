from django.db import models
from django.conf import settings


# ── Categorías de alerta ──────────────────────────────────────────────────────
CATEGORY_CHOICES = [
    ('critico',     'Crítico'),
    ('alto',        'Alto'),
    ('informativo', 'Informativo'),
]

# ── Origen del evento ─────────────────────────────────────────────────────────
ORIGIN_CHOICES = [
    ('maestro', 'Maestro'),
    ('esclavo', 'Esclavo'),
]

# ── Estado del sensor ─────────────────────────────────────────────────────────
ESTADO_CHOICES = [
    ('normal', 'Normal'),
    ('activo', 'Activo'),
]

# ── Claves internas de sensores (índice = posición en el payload) ─────────────
SENSOR_KEYS = [
    ('puerta_tablero',  'Puerta tablero'),
    ('puerta_externa',  'Puerta externa'),
    ('pir1',            'PIR 1'),
    ('pir2',            'PIR 2'),
    ('pir3',            'PIR 3'),
    ('pir4',            'PIR 4'),
    ('vibracion',       'Vibración'),
    ('flama',           'Flama'),
    ('puerta_auxiliar', 'Puerta auxiliar'),
    ('puerta_esclavo',  'Puerta esclavo (remota)'),
]


class SecurityDevice(models.Model):
    """Dispositivo maestro de seguridad de ambiente controlado."""

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='security_devices',
    )
    DateCreate = models.DateTimeField('Fecha de registro', auto_now_add=True)

    Name        = models.CharField('Nombre del dispositivo', max_length=100, unique=True)
    Description = models.TextField('Descripción', max_length=500, blank=True, null=True)
    MacAddress  = models.CharField('MAC Address', max_length=17, unique=True, blank=True, null=True)
    Location    = models.CharField('Ubicación', max_length=200, blank=True, null=True)

    # Configuración MQTT
    MqttBroker  = models.CharField('Broker MQTT', max_length=200, blank=True, null=True,
                                    help_text='IP o hostname del broker, ej. 192.168.1.100')
    MqttPort    = models.PositiveIntegerField('Puerto MQTT', default=1883)
    MqttTopic   = models.CharField('Topic de escucha', max_length=300, blank=True, null=True,
                                    help_text='Topic MQTT, ej. seguridad/maestro01/# o seguridad/critico')

    Status      = models.CharField(
        'Estado', max_length=20,
        choices=[('Active', 'Activo'), ('Inactive', 'Inactivo'), ('Maintenance', 'Mantenimiento')],
        default='Active',
    )

    # Estado en tiempo real (actualizado por MQTT)
    BuzzerState   = models.CharField('Buzzer', max_length=20, default='reposo', blank=True)
    BypassState   = models.BooleanField('Bypass', default=False)
    Temperature   = models.FloatField('Temperatura (°C)', null=True, blank=True)
    Humidity      = models.FloatField('Humedad (%)', null=True, blank=True)
    HasRTC        = models.BooleanField('RTC disponible', default=False)
    SDStatus      = models.CharField('Estado SD', max_length=50, blank=True, null=True)
    WifiOK        = models.BooleanField('WiFi OK', default=False)
    MqttOK        = models.BooleanField('MQTT OK', default=False)
    LastSeen      = models.DateTimeField('Última conexión', null=True, blank=True)

    class Meta:
        verbose_name = 'Dispositivo de seguridad'
        verbose_name_plural = 'Dispositivos de seguridad'
        ordering = ['Name']

    def __str__(self):
        return self.Name


class Sensor(models.Model):
    """Configuración individual de cada sensor de un dispositivo."""

    Device   = models.ForeignKey(
        SecurityDevice, on_delete=models.CASCADE, related_name='sensors',
    )
    SensorKey    = models.CharField('Clave', max_length=30, choices=SENSOR_KEYS)
    Name         = models.CharField('Nombre', max_length=60)
    SensorIndex  = models.PositiveSmallIntegerField('Índice (payload)', default=0)
    Enabled      = models.BooleanField('Habilitado', default=False)
    Category     = models.CharField('Categoría', max_length=20,
                                    choices=CATEGORY_CHOICES, default='critico')
    # Estado en tiempo real
    CurrentState = models.CharField('Estado actual', max_length=20, default='normal')

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        unique_together = ('Device', 'SensorKey')
        ordering = ['SensorIndex']

    def __str__(self):
        return f'{self.Device.Name} – {self.Name}'

    @property
    def category_display(self):
        return dict(CATEGORY_CHOICES).get(self.Category, self.Category)


class EventLog(models.Model):
    """Registro de eventos enviados por el dispositivo vía MQTT."""

    Device          = models.ForeignKey(
        SecurityDevice, on_delete=models.CASCADE, related_name='events',
    )
    ServerTimestamp = models.DateTimeField('Timestamp servidor', auto_now_add=True)
    DeviceTimestamp = models.DateTimeField('Timestamp dispositivo', null=True, blank=True)

    Origin      = models.CharField('Origen', max_length=20,
                                   choices=ORIGIN_CHOICES, default='maestro')
    SensorIndex = models.PositiveSmallIntegerField('Sensor (índice)', null=True, blank=True)
    SensorName  = models.CharField('Nombre sensor', max_length=60, blank=True, null=True)
    Estado      = models.CharField('Estado', max_length=20,
                                   choices=ESTADO_CHOICES, default='normal')
    Category    = models.CharField('Categoría', max_length=20,
                                   choices=CATEGORY_CHOICES, default='informativo')
    User        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='security_events',
    )
    Canal = models.CharField('Canal', max_length=20, blank=True, null=True,
                             help_text='wifi / gprs / —')
    Notes = models.CharField('Notas', max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Evento de seguridad'
        verbose_name_plural = 'Eventos de seguridad'
        ordering = ['-ServerTimestamp']

    def __str__(self):
        return f'{self.Device.Name} | {self.SensorName} | {self.Estado} | {self.ServerTimestamp:%Y-%m-%d %H:%M}'

    @property
    def category_color(self):
        return {'critico': 'danger', 'alto': 'warning', 'informativo': 'info'}.get(self.Category, 'secondary')
