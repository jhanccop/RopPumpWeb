from django.conf import settings
from django.db import models

from .managers import (
    BatteryManager,
    TankManager,
    WellManager,
    WellDailyProductionManager,
    OperationalAlertManager,
)


# ---------------------------------------------------------------------------
# Battery  (gathering station)
# ---------------------------------------------------------------------------

class Battery(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_battery_owner',
    )

    Name = models.CharField('Name', max_length=150, unique=True)
    Code = models.CharField('Code', max_length=50, unique=True)
    Description = models.TextField('Description', blank=True, null=True)
    Location = models.CharField('Location', max_length=200, blank=True)

    Latitude = models.FloatField('Latitude', null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)

    STATUS_CHOICES = (
        ('active',       'Activa'),
        ('inactive',     'Inactiva'),
        ('maintenance',  'Mantenimiento'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    DateCreate = models.DateTimeField(auto_now_add=True)

    objects = BatteryManager()

    class Meta:
        ordering = ['Name']
        verbose_name = 'Batería'
        verbose_name_plural = 'Baterías'

    def __str__(self):
        return f'{self.Code} – {self.Name}'


# ---------------------------------------------------------------------------
# Manifold
# ---------------------------------------------------------------------------

class Manifold(models.Model):
    id = models.BigAutoField(primary_key=True)

    Battery = models.ForeignKey(
        'Battery',
        on_delete=models.CASCADE,
        related_name='manifolds',
    )

    Name = models.CharField('Name', max_length=100)
    Code = models.CharField('Code', max_length=50)

    MaxPressure = models.FloatField('Max Pressure (PSI)', null=True, blank=True)

    STATUS_CHOICES = (
        ('active',   'Activo'),
        ('inactive', 'Inactivo'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    DateCreate = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('Battery', 'Code')
        verbose_name = 'Manifold'
        verbose_name_plural = 'Manifolds'

    def __str__(self):
        return f'{self.Battery.Code}-{self.Code}'


# ---------------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------------

class Tank(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_tank_owner',
    )

    Battery = models.ForeignKey(
        'Battery',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tanks',
    )

    Name = models.CharField('Name', max_length=150)
    Code = models.CharField('Code', max_length=50, unique=True)

    TYPE_CHOICES = (
        ('oil',      'Petróleo'),
        ('water',    'Agua'),
        ('slop',     'Slop'),
        ('chemical', 'Químico'),
    )
    Type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default='oil')

    NominalCapacity = models.FloatField('Nominal Capacity (bbl)')
    WorkingCapacity = models.FloatField('Working Capacity (bbl)', null=True, blank=True)

    MATERIAL_CHOICES = (
        ('steel',       'Acero'),
        ('fiberglass',  'Fibra de vidrio'),
        ('concrete',    'Concreto'),
    )
    Material = models.CharField(
        'Material', max_length=20,
        choices=MATERIAL_CHOICES,
        default='steel',
    )

    Diameter = models.FloatField('Diameter (m)', null=True, blank=True)
    Height   = models.FloatField('Height (m)',   null=True, blank=True)

    SENSOR_TYPE_CHOICES = (
        ('manual',     'Manual'),
        ('ultrasonic', 'Ultrasónico'),
        ('radar',      'Radar'),
        ('pressure',   'Presión'),
    )
    SensorType = models.CharField(
        'Sensor Type', max_length=20,
        choices=SENSOR_TYPE_CHOICES,
        default='manual',
    )

    LowLevelAlert  = models.FloatField('Low Level Alert (%)',  null=True, blank=True)
    HighLevelAlert = models.FloatField('High Level Alert (%)', null=True, blank=True)

    InstallationDate = models.DateField('Installation Date', null=True, blank=True)

    STATUS_CHOICES = (
        ('active',      'Activa'),
        ('inactive',    'Inactiva'),
        ('maintenance', 'Mantenimiento'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    Latitude  = models.FloatField('Latitude',  null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)

    DateCreate = models.DateTimeField(auto_now_add=True)

    objects = TankManager()

    class Meta:
        ordering = ['Battery', 'Name']
        verbose_name = 'Tanque'
        verbose_name_plural = 'Tanques'

    def __str__(self):
        return f'{self.Code} – {self.Name}'


# ---------------------------------------------------------------------------
# TankCalibration  (gauging table)
# ---------------------------------------------------------------------------

class TankCalibration(models.Model):
    id = models.BigAutoField(primary_key=True)

    Tank = models.ForeignKey(
        'Tank',
        on_delete=models.CASCADE,
        related_name='calibrations',
    )

    Level  = models.FloatField('Level (cm)')
    Volume = models.FloatField('Volume (bbl)')

    class Meta:
        ordering = ['Tank', 'Level']
        unique_together = ('Tank', 'Level')
        verbose_name = 'Calibración de Tanque'
        verbose_name_plural = 'Calibraciones de Tanque'

    def __str__(self):
        return f'{self.Tank.Code} {self.Level}cm={self.Volume}bbl'


# ---------------------------------------------------------------------------
# PumpingUnit  (mechanical pumping unit specs)
# ---------------------------------------------------------------------------

class PumpingUnit(models.Model):
    id = models.BigAutoField(primary_key=True)

    Name = models.CharField('Name', max_length=150)
    Code = models.CharField('Code', max_length=50, unique=True)

    TYPE_CHOICES = (
        ('beam',      'Bombeo Mecánico'),
        ('pcp',       'PCP'),
        ('bes',       'BES'),
        ('hydraulic', 'Hidráulico'),
    )
    Type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES, default='beam')

    Manufacturer = models.CharField('Manufacturer', max_length=100, blank=True)
    Model        = models.CharField('Model',        max_length=100, blank=True)

    StrokeLength  = models.FloatField('Stroke Length (in)',   null=True, blank=True)
    MaxSPM        = models.FloatField('Max SPM',              null=True, blank=True)
    MaxLoad       = models.FloatField('Max Load (lbs)',       null=True, blank=True)
    MotorPower    = models.FloatField('Motor Power (HP)',     null=True, blank=True)
    GearboxRating = models.FloatField('Gearbox Rating (in-lbs)', null=True, blank=True)

    InstallationDate = models.DateField('Installation Date', null=True, blank=True)

    STATUS_CHOICES = (
        ('operational', 'Operativo'),
        ('maintenance', 'Mantenimiento'),
        ('stopped',     'Detenido'),
        ('fault',       'Falla'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='operational',
    )

    DateCreate = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidad de Bombeo'
        verbose_name_plural = 'Unidades de Bombeo'

    def __str__(self):
        return f'{self.Code} – {self.Name}'


# ---------------------------------------------------------------------------
# Well  (oil well — central model)
# ---------------------------------------------------------------------------

class Well(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_well_owner',
    )

    Battery = models.ForeignKey(
        'Battery',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='wells',
    )

    Manifold = models.ForeignKey(
        'Manifold',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='wells',
    )

    Tank = models.ForeignKey(
        'Tank',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='wells',
    )

    PumpingUnit = models.ForeignKey(
        'PumpingUnit',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='wells',
    )

    AnalyzerDevice = models.ForeignKey(
        'device.WellAnalyzerDevice',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_wells',
        verbose_name='Well Analyzer Device',
    )

    Code      = models.CharField('Code',       max_length=50,  unique=True)
    Name      = models.CharField('Name',       max_length=150)
    FieldName = models.CharField('Field Name', max_length=100, blank=True)
    Description = models.TextField('Description', blank=True, null=True)

    TotalDepth   = models.FloatField('Total Depth (m)',     null=True, blank=True)
    PumpDepth    = models.FloatField('Pump Depth (m)',      null=True, blank=True)
    PumpDiameter = models.FloatField('Pump Diameter (in)', null=True, blank=True)

    LIFT_CHOICES = (
        ('mechanical',   'Bombeo Mecánico'),
        ('pcp',          'PCP'),
        ('bes',          'BES'),
        ('natural_flow', 'Flujo Natural'),
        ('gas_lift',     'Gas Lift'),
    )
    LiftType = models.CharField(
        'Lift Type', max_length=20,
        choices=LIFT_CHOICES,
        default='mechanical',
    )

    InstallationDate  = models.DateField('Installation Date', null=True, blank=True)
    ProductionTarget  = models.FloatField('Production Target (bbl/day)', null=True, blank=True)

    STATUS_CHOICES = (
        ('active',       'Activo'),
        ('inactive',     'Inactivo'),
        ('abandoned',    'Abandonado'),
        ('portable',     'Portátil'),
    )
    Status = models.CharField(
        'Status', max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    Latitude  = models.FloatField('Latitude',  null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)

    Notes = models.TextField('Notes', blank=True, null=True)

    DateCreate = models.DateTimeField(auto_now_add=True)
    DateUpdate = models.DateTimeField(auto_now=True)

    objects = WellManager()

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Pozo'
        verbose_name_plural = 'Pozos'

    def __str__(self):
        return f'{self.Code} – {self.Name}'

    @property
    def is_producing(self):
        return self.Status == 'producing'


# ---------------------------------------------------------------------------
# WellDailyProduction
# ---------------------------------------------------------------------------

class WellDailyProduction(models.Model):
    id = models.BigAutoField(primary_key=True)

    Well = models.ForeignKey(
        'Well',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='daily_productions',
    )

    EnteredBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='productions_entered',
    )

    OperativeDate = models.DateField('Fecha Operativa')

    OilProduction   = models.FloatField('Oil Production (bbl)',   null=True, blank=True)
    WaterProduction = models.FloatField('Water Production (bbl)', null=True, blank=True)
    GasProduction   = models.FloatField('Gas Production (MSCF)',  null=True, blank=True)

    RunTime = models.FloatField('Run Time (hours)', null=True, blank=True)
    SPM     = models.FloatField('SPM',              null=True, blank=True)
    Fillage = models.FloatField('Fillage (%)',       null=True, blank=True)

    CONDITION_CHOICES = (
        ('normal',       'Normal'),
        ('pump_off',     'Pump Off'),
        ('gas_lock',     'Gas Lock'),
        ('low_fillage',  'Bajo Llenado'),
        ('maintenance',  'Mantenimiento'),
        ('stopped',      'Detenido'),
        ('other',        'Otro'),
    )
    OperationalCondition = models.CharField(
        'Operational Condition', max_length=20,
        choices=CONDITION_CHOICES,
        default='normal',
    )

    DeferredProduction = models.FloatField('Deferred Production (bbl)', default=0)

    # Tank inventory ─────────────────────────────────────────────────────────
    Tank           = models.ForeignKey(
        'Tank',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='daily_productions',
        verbose_name='Tanque receptor',
    )
    TankLevelStart = models.FloatField('Nivel tanque inicio (bbl)', null=True, blank=True)
    TankLevelEnd   = models.FloatField('Nivel tanque fin (bbl)',    null=True, blank=True)
    TankProduction = models.FloatField('Producción en tanque (bbl)', null=True, blank=True)

    Observations = models.TextField('Observations', blank=True, null=True)

    DateCreate = models.DateTimeField(auto_now_add=True)

    objects = WellDailyProductionManager()

    class Meta:
        ordering = ['-OperativeDate', '-DateCreate']
        unique_together = ('Tank', 'OperativeDate')
        verbose_name = 'Producción Diaria'
        verbose_name_plural = 'Producciones Diarias'

    def __str__(self):
        asset = self.Tank.Code if self.Tank else (self.Well.Code if self.Well else '—')
        return f'{asset} {self.OperativeDate}'

    @property
    def TotalProduction(self):
        return (self.OilProduction or 0) + (self.WaterProduction or 0)

    @property
    def WaterCut(self):
        total = self.TotalProduction
        if self.WaterProduction and total:
            return self.WaterProduction / total * 100
        return None


# ---------------------------------------------------------------------------
# TankReading
# ---------------------------------------------------------------------------

class TankReading(models.Model):
    id = models.BigAutoField(primary_key=True)

    Tank = models.ForeignKey(
        'Tank',
        on_delete=models.CASCADE,
        related_name='readings',
    )

    ReadingDate = models.DateTimeField('Reading Date')
    Level       = models.FloatField('Level (cm)')
    Temperature = models.FloatField('Temperature (°C)', null=True, blank=True)
    WaterLevel  = models.FloatField('Water Level (cm)', null=True, blank=True)
    Volume      = models.FloatField('Volume (bbl)',     null=True, blank=True)

    SOURCE_CHOICES = (
        ('manual', 'Manual'),
        ('iot',    'IoT'),
        ('scada',  'SCADA'),
    )
    Source = models.CharField(
        'Source', max_length=10,
        choices=SOURCE_CHOICES,
        default='manual',
    )

    Notes = models.CharField('Notes', max_length=200, blank=True)

    EnteredBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tank_readings_entered',
    )

    DateCreate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ReadingDate']
        verbose_name = 'Lectura de Tanque'
        verbose_name_plural = 'Lecturas de Tanque'
        indexes = [
            models.Index(fields=['Tank', 'ReadingDate']),
        ]

    def __str__(self):
        return f'{self.Tank.Code} {self.ReadingDate:%Y-%m-%d %H:%M}'

    @property
    def LevelPercent(self):
        try:
            if self.Tank.Height:
                return self.Level / (self.Tank.Height * 100) * 100
        except (AttributeError, ZeroDivisionError, TypeError):
            pass
        return None


# ---------------------------------------------------------------------------
# PumpingReading  (IoT telemetry time-series)
# ---------------------------------------------------------------------------

class PumpingReading(models.Model):
    id = models.BigAutoField(primary_key=True)

    Well = models.ForeignKey(
        'Well',
        on_delete=models.CASCADE,
        related_name='pumping_readings',
    )

    DateCreate = models.DateTimeField(auto_now_add=True)

    SPM              = models.FloatField('SPM',                         null=True, blank=True)
    Fillage          = models.FloatField('Fillage (%)',                  null=True, blank=True)
    RunTime          = models.FloatField('Run Time (hours)',             null=True, blank=True)
    OilProduction    = models.FloatField('Oil Production (bbl/day)',     null=True, blank=True)
    WaterProduction  = models.FloatField('Water Production (bbl/day)',   null=True, blank=True)
    Torque           = models.FloatField('Torque (ft-lbs)',              null=True, blank=True)
    MotorCurrent     = models.FloatField('Motor Current (A)',            null=True, blank=True)
    Vibration        = models.FloatField('Vibration (mm/s)',             null=True, blank=True)
    Temperature      = models.FloatField('Temperature (°C)',             null=True, blank=True)
    DynamicLevel     = models.FloatField('Dynamic Level (m)',            null=True, blank=True)
    VolumetricEfficiency = models.FloatField('Volumetric Efficiency (%)', null=True, blank=True)

    STATUS_CHOICES = (
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
    OperationalStatus = models.CharField(
        'Operational Status', max_length=20,
        choices=STATUS_CHOICES,
        default='producing',
    )

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Lectura de Bombeo'
        verbose_name_plural = 'Lecturas de Bombeo'
        indexes = [
            models.Index(fields=['Well', 'DateCreate']),
        ]


# ---------------------------------------------------------------------------
# OperationalAlert
# ---------------------------------------------------------------------------

class OperationalAlert(models.Model):
    id = models.BigAutoField(primary_key=True)

    Well = models.ForeignKey(
        'Well',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='alerts',
    )

    Tank = models.ForeignKey(
        'Tank',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='alerts',
    )

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_alerts_owner',
    )

    ALERT_TYPE_CHOICES = (
        ('low_fillage',          'Bajo Llenado'),
        ('tank_overflow',        'Sobrellenado Tanque'),
        ('low_production',       'Baja Producción'),
        ('high_temperature',     'Alta Temperatura'),
        ('overcurrent',          'Sobrecorriente'),
        ('sensor_fault',         'Falla de Sensor'),
        ('abnormal_production',  'Producción Anormal'),
        ('well_stopped',         'Pozo Detenido'),
        ('high_water_cut',       'Exceso de Agua'),
        ('pump_off',             'Pump Off'),
        ('gas_lock',             'Gas Lock'),
        ('low_tank_level',       'Bajo Nivel Tanque'),
    )
    AlertType = models.CharField('Alert Type', max_length=30, choices=ALERT_TYPE_CHOICES)

    SEVERITY_CHOICES = (
        ('low',      'Baja'),
        ('medium',   'Media'),
        ('high',     'Alta'),
        ('critical', 'Crítica'),
    )
    Severity = models.CharField(
        'Severity', max_length=15,
        choices=SEVERITY_CHOICES,
        default='medium',
    )

    Variable       = models.CharField('Variable',        max_length=100, blank=True)
    DetectedValue  = models.FloatField('Detected Value',  null=True, blank=True)
    ThresholdValue = models.FloatField('Threshold Value', null=True, blank=True)
    Message        = models.CharField('Message',          max_length=400)

    STATUS_CHOICES = (
        ('active',       'Activa'),
        ('acknowledged', 'Atendida'),
        ('closed',       'Cerrada'),
    )
    Status = models.CharField(
        'Status', max_length=15,
        choices=STATUS_CHOICES,
        default='active',
    )

    AcknowledgedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_acknowledged_alerts',
    )

    DateCreate       = models.DateTimeField(auto_now_add=True)
    DateAcknowledged = models.DateTimeField('Date Acknowledged', null=True, blank=True)
    DateClosed       = models.DateTimeField('Date Closed',       null=True, blank=True)

    objects = OperationalAlertManager()

    class Meta:
        ordering = ['-DateCreate']
        verbose_name = 'Alarma Operacional'
        verbose_name_plural = 'Alarmas Operacionales'

    def __str__(self):
        asset = self.Well or self.Tank
        asset_code = asset.Code if asset else '—'
        return f'{asset_code} [{self.get_AlertType_display()}] {self.get_Severity_display()}'


# ---------------------------------------------------------------------------
# AlertRule
# ---------------------------------------------------------------------------

class AlertRule(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='oilfield_alert_rules_owner',
    )

    ASSET_TYPE_CHOICES = (
        ('well',  'Pozo'),
        ('tank',  'Tanque'),
    )
    AssetType = models.CharField('Asset Type', max_length=10, choices=ASSET_TYPE_CHOICES)

    Well = models.ForeignKey(
        'Well',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='alert_rules',
    )

    Tank = models.ForeignKey(
        'Tank',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='alert_rules',
    )

    VARIABLE_CHOICES = (
        # Well variables
        ('SPM',                  'SPM'),
        ('Fillage',              'Llenado %'),
        ('OilProduction',        'Prod. Oil'),
        ('WaterProduction',      'Prod. Agua'),
        ('RunTime',              'Run Time'),
        ('Torque',               'Torque'),
        ('MotorCurrent',         'Corriente Motor'),
        ('Vibration',            'Vibración'),
        ('Temperature',          'Temperatura'),
        ('DynamicLevel',         'Nivel Dinámico'),
        ('VolumetricEfficiency', 'Efic. Volumétrica'),
        # Tank variables
        ('Level',                'Nivel cm'),
        ('LevelPercent',         'Nivel %'),
        ('WaterLevel',           'Nivel Agua'),
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

    ALERT_TYPE_CHOICES = (
        ('low_fillage',         'Bajo Llenado'),
        ('tank_overflow',       'Sobrellenado Tanque'),
        ('low_production',      'Baja Producción'),
        ('high_temperature',    'Alta Temperatura'),
        ('overcurrent',         'Sobrecorriente'),
        ('sensor_fault',        'Falla de Sensor'),
        ('abnormal_production', 'Producción Anormal'),
        ('well_stopped',        'Pozo Detenido'),
        ('high_water_cut',      'Exceso de Agua'),
        ('pump_off',            'Pump Off'),
        ('gas_lock',            'Gas Lock'),
        ('low_tank_level',      'Bajo Nivel Tanque'),
    )
    AlertType = models.CharField('Alert Type', max_length=30, choices=ALERT_TYPE_CHOICES)

    SEVERITY_CHOICES = (
        ('low',      'Baja'),
        ('medium',   'Media'),
        ('high',     'Alta'),
        ('critical', 'Crítica'),
    )
    Severity = models.CharField('Severity', max_length=15, choices=SEVERITY_CHOICES)

    IsActive    = models.BooleanField('Is Active', default=True)
    Description = models.CharField('Description', max_length=200, blank=True)
    DateCreate  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Regla de Alerta'
        verbose_name_plural = 'Reglas de Alerta'

    def __str__(self):
        return f'{self.AssetType} | {self.get_Variable_display()} {self.get_Condition_display()} {self.Threshold}'


# ---------------------------------------------------------------------------
# WellEvent
# ---------------------------------------------------------------------------

class WellEvent(models.Model):
    id = models.BigAutoField(primary_key=True)

    Well = models.ForeignKey(
        'Well',
        on_delete=models.CASCADE,
        related_name='events',
    )

    EnteredBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='well_events_entered',
    )

    EVENT_TYPE_CHOICES = (
        ('start',            'Arranque'),
        ('stop',             'Parada'),
        ('maintenance',      'Mantenimiento'),
        ('observation',      'Observación'),
        ('repair',           'Reparación'),
        ('workover',         'Workover'),
        ('inspection',       'Inspección'),
        ('parameter_change', 'Cambio Parámetros'),
    )
    EventType = models.CharField('Event Type', max_length=20, choices=EVENT_TYPE_CHOICES)

    EventDate   = models.DateTimeField('Event Date')
    Description = models.TextField('Description')

    DateCreate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-EventDate']
        verbose_name = 'Evento del Pozo'
        verbose_name_plural = 'Eventos del Pozo'

    def __str__(self):
        return f'{self.Well.Code} {self.get_EventType_display()} {self.EventDate:%Y-%m-%d}'
