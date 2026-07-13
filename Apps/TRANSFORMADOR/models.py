from datetime import date

from django.conf import settings
from django.db import models

from .managers import TransformerManager, SubstationManager, AlertManager


# ---------------------------------------------------------------------------
# Substation
# ---------------------------------------------------------------------------

class Substation(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='substation_owner',
    )

    Name = models.CharField('Name', max_length=150, unique=True)
    Description = models.TextField('Description', blank=True, null=True)

    TYPE_CHOICES = (
        ('primary',   'Primaria'),
        ('secondary', 'Secundaria'),
        ('mobile',    'Móvil'),
    )
    Type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES)

    STATUS_CHOICES = (
        ('operational', 'Operativo'),
        ('maintenance', 'Mantenimiento'),
        ('fault',       'Falla'),
        ('inactive',    'Inactivo'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='operational',
    )

    NominalVoltage    = models.DecimalField('Nominal Voltage (kV)',    max_digits=10, decimal_places=2, null=True, blank=True)
    InstalledCapacity = models.DecimalField('Installed Capacity (MVA)', max_digits=10, decimal_places=2, null=True, blank=True)

    Latitude  = models.FloatField('Latitude',  null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)
    Address   = models.CharField('Address', max_length=300, blank=True)

    DateCreate = models.DateTimeField(auto_now_add=True)

    objects = SubstationManager()

    class Meta:
        ordering = ['Name']
        verbose_name = 'Subestación'
        verbose_name_plural = 'Subestaciones'

    def __str__(self):
        return self.Name


# ---------------------------------------------------------------------------
# Transformer
# ---------------------------------------------------------------------------

class Transformer(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='transformer_owner',
    )

    Code       = models.CharField('Code',         max_length=50,  unique=True)
    Series     = models.CharField('Series',       max_length=100, blank=True)
    StationName = models.CharField('Station Name', max_length=150)
    Description = models.TextField('Description', blank=True, null=True)

    NominalPower     = models.DecimalField('Nominal Power (kVA)',      max_digits=10, decimal_places=2)
    PrimaryVoltage   = models.DecimalField('Primary Voltage (V)',      max_digits=10, decimal_places=2)
    SecondaryVoltage = models.DecimalField('Secondary Voltage (V)',    max_digits=10, decimal_places=2)

    TYPE_CHOICES = (
        ('distribution',    'Distribución'),
        ('power',           'Potencia'),
        ('measurement',     'Medida'),
        ('autotransformer', 'Autotransformador'),
    )
    Type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES)

    COOLING_CHOICES = (
        ('ONAN', 'ONAN'),
        ('ONAF', 'ONAF'),
        ('OFAF', 'OFAF'),
        ('dry',  'Seco'),
    )
    CoolingType = models.CharField(
        'Cooling Type', max_length=10,
        choices=COOLING_CHOICES,
        default='ONAN',
    )

    Manufacturer    = models.CharField('Manufacturer', max_length=100, blank=True)
    Model           = models.CharField('Model',        max_length=100, blank=True)
    YearManufacture = models.PositiveSmallIntegerField('Year of Manufacture', null=True, blank=True)
    InstallationDate = models.DateField('Installation Date', null=True, blank=True)
    EstimatedLifespan = models.PositiveSmallIntegerField('Estimated Lifespan (years)', default=25)

    STATUS_CHOICES = (
        ('operational', 'Operativo'),
        ('maintenance', 'Mantenimiento'),
        ('fault',       'Falla'),
        ('inactive',    'Inactivo'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='operational',
    )

    Latitude  = models.FloatField('Latitude',  null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)
    Address   = models.CharField('Address', max_length=300, blank=True)

    Substation = models.ForeignKey(
        Substation,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='transformers',
    )

    DateCreate = models.DateTimeField(auto_now_add=True)
    DateUpdate = models.DateTimeField(auto_now=True)

    objects = TransformerManager()

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Transformador'
        verbose_name_plural = 'Transformadores'

    def __str__(self):
        return f'{self.Code} – {self.StationName}'

    @property
    def age(self):
        """Returns the age in years since InstallationDate, or None."""
        if not self.InstallationDate:
            return None
        today = date.today()
        delta = today - self.InstallationDate
        return delta.days // 365


# ---------------------------------------------------------------------------
# ElectricalReading  (telemetry time-series)
# ---------------------------------------------------------------------------

class ElectricalReading(models.Model):
    id = models.BigAutoField(primary_key=True)

    Transformer = models.ForeignKey(
        Transformer,
        on_delete=models.CASCADE,
        related_name='readings',
    )
    DateCreate = models.DateTimeField(auto_now_add=True)

    # Temperatures (°C)
    # OTI: Oil Temperature Indicator — temperatura aceite superior (tapa)
    OilTemperature     = models.FloatField('Temperatura Aceite Superior OTI (°C)', null=True, blank=True)
    # Hot Spot: temperatura punto caliente del devanado (estimada o medida por fibra óptica)
    HotSpotTemperature = models.FloatField('Temperatura Hot Spot Devanado (°C)',   null=True, blank=True)
    AmbientTemperature = models.FloatField('Temperatura Ambiente (°C)',             null=True, blank=True)

    # Mechanical / condition monitoring
    # InternalPressure: presión interna del tanque / activación PRD (kPa)
    InternalPressure = models.FloatField('Presión Interna / PRD (kPa)', null=True, blank=True)
    OilLevel         = models.FloatField('Nivel de Aceite (%)',          null=True, blank=True)
    Vibration        = models.FloatField('Vibración (mm/s)',              null=True, blank=True)
    # OilHumidity: humedad relativa en el aceite (ppm o %)
    OilHumidity      = models.FloatField('Humedad en Aceite (ppm)',       null=True, blank=True)

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Lectura Eléctrica'
        verbose_name_plural = 'Lecturas Eléctricas'
        indexes = [
            models.Index(fields=['Transformer', 'DateCreate']),
        ]

    def __str__(self):
        return f'{self.Transformer} — {self.DateCreate:%Y-%m-%d %H:%M}'



# ---------------------------------------------------------------------------
# AlertRule
# ---------------------------------------------------------------------------

class AlertRule(models.Model):
    id = models.BigAutoField(primary_key=True)

    Transformer = models.ForeignKey(
        Transformer,
        on_delete=models.CASCADE,
        related_name='alert_rules',
    )

    VARIABLE_CHOICES = (
        ('OilTemperature',     'Temperatura Aceite Superior OTI (°C)'),
        ('HotSpotTemperature', 'Temperatura Hot Spot Devanado (°C)'),
        ('AmbientTemperature', 'Temperatura Ambiente (°C)'),
        ('InternalPressure',   'Presión Interna / PRD (kPa)'),
        ('OilLevel',           'Nivel de Aceite (%)'),
        ('Vibration',          'Vibración (mm/s)'),
        ('OilHumidity',        'Humedad en Aceite (ppm)'),
    )
    Variable = models.CharField('Variable', max_length=30, choices=VARIABLE_CHOICES)

    CONDITION_CHOICES = (
        ('gt',  'Mayor que'),
        ('lt',  'Menor que'),
        ('gte', 'Mayor o igual'),
        ('lte', 'Menor o igual'),
    )
    Condition = models.CharField('Condition', max_length=5, choices=CONDITION_CHOICES)

    Threshold = models.FloatField('Threshold')

    SEVERITY_CHOICES = (
        ('warning',   'Advertencia'),
        ('critical',  'Crítico'),
        ('emergency', 'Emergencia'),
    )
    Severity = models.CharField('Severity', max_length=15, choices=SEVERITY_CHOICES)

    IsActive    = models.BooleanField('Is Active', default=True)
    Description = models.CharField('Description', max_length=200, blank=True)
    DateCreate  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['Transformer', 'Variable']
        verbose_name = 'Regla de Alerta'
        verbose_name_plural = 'Reglas de Alerta'
        unique_together = ('Transformer', 'Variable', 'Condition')

    def __str__(self):
        return f'{self.Transformer} | {self.get_Variable_display()} {self.get_Condition_display()} {self.Threshold}'


# ---------------------------------------------------------------------------
# Alert
# ---------------------------------------------------------------------------

class Alert(models.Model):
    id = models.BigAutoField(primary_key=True)

    Transformer = models.ForeignKey(
        Transformer,
        on_delete=models.CASCADE,
        related_name='alerts',
    )
    Rule = models.ForeignKey(
        AlertRule,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='triggered_alerts',
    )

    Variable = models.CharField('Variable', max_length=100)

    SEVERITY_CHOICES = (
        ('warning',   'Advertencia'),
        ('critical',  'Crítico'),
        ('emergency', 'Emergencia'),
    )
    Severity = models.CharField('Severity', max_length=15, choices=SEVERITY_CHOICES)

    DetectedValue  = models.FloatField('Detected Value')
    ThresholdValue = models.FloatField('Threshold Value')
    Message        = models.CharField('Message', max_length=300)

    STATUS_CHOICES = (
        ('active',       'Activa'),
        ('acknowledged', 'Atendida'),
        ('closed',       'Cerrada'),
    )
    Status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='active')

    AcknowledgedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='acknowledged_alerts',
    )

    DateCreate      = models.DateTimeField(auto_now_add=True)
    DateAcknowledged = models.DateTimeField('Date Acknowledged', null=True, blank=True)
    DateClosed      = models.DateTimeField('Date Closed',       null=True, blank=True)

    objects = AlertManager()

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'

    def __str__(self):
        return f'{self.Transformer} — {self.Variable} [{self.get_Severity_display()}]'
