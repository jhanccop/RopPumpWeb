from wsgiref.handlers import format_date_time
from django.db import models
from django.conf import settings

from Apps.field.models import Field
from Apps.batteries.models import Battery
from Apps.groups.models import Group

from .managers import WellManager

class EngineType(models.Model):
    id = models.BigAutoField(primary_key=True)
    ENGINE_CHOICES = (
        ("Electric", "Electric"),
        ("Gas", "Gas"),
    )
    EngineType = models.CharField('Engine Type', max_length=20, choices=ENGINE_CHOICES, default="Gas")
    EnginePower = models.FloatField('Engine Power', null=True, blank =True)
    EngineBrand = models.CharField('Engine Brand', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Engine Type'
        verbose_name_plural = 'Engine Types'

    def __str__(self):
        return self.EngineType


class RodPumpInstallation(models.Model):
    id = models.BigAutoField(primary_key=True)

    # SURFACE DATA
    StrokeLength = models.FloatField('Stroke Length', null=True, blank =True)
    PolishedRodDiameter = models.FloatField('Polished Rod Diameter', null=True, blank =True)
    IdEngineTYpe = models.ForeignKey(EngineType, on_delete=models.CASCADE, unique=False,blank=True)
    
    PlungerDiameter = models.FloatField('Plunger Diameter', null=True, blank =True)
    TotalRodLength = models.FloatField('Total Rod Length', null=True, blank =True)
    TotalRodWeight = models.FloatField('Total Rod Weight', null=True, blank =True)
    
    ProductionTime = models.FloatField('Production Time', null=True, blank =True)
    RestTime = models.FloatField('Rest Time', null=True, blank =True)
    
class well(models.Model):
    id = models.BigAutoField(primary_key=True)
    DateCreate = models.DateTimeField(auto_now_add= True )
    PumpName = models.CharField('Pump Name', max_length=100, unique=True)
    FieldName = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False,blank=True)
    BatteryName = models.ForeignKey(Battery, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    GroupName = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    Location = models.CharField('Location', max_length=100)
    SupervisorUser = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    InstallationDate = models.DateField(auto_now_add = False)
    InstallationComment = models.TextField('Installation Comment', max_length=500)
    
    TYPE_CHOICES = (
        ("Sucker Rod Pump", "Sucker Rod Pump"),
        ("Plunger Lift", "Plunger Lift"),
        ("Electrical Submersible Pump", "Electrical Submersible Pump"),
    )
    PumpType = models.CharField('Pump Type', max_length=50, choices=TYPE_CHOICES, default="Rod Pump")
    
    PumpIntake = models.FloatField('Pump Intake', null=True, blank =True)
    MeasuredDepth = models.FloatField('Measured Depth', null=True, blank =True)
    
    IdInstallation = models.ForeignKey(RodPumpInstallation, on_delete=models.CASCADE, unique=False,blank=True)

    STATUS_CHOICES = (
        ("Normal Running", "Normal Running"),
        ("Maintance", "Maintance"),
    )
    DesignStatus = models.CharField('Design Status', max_length=50, choices=STATUS_CHOICES, default="Normal Running")
    
   
    # Monitoring data
    Status_CHOICES = (
        ("stopped", "stopped"),
        ("running", "running"),
        ("low battery", "low battery"),
        ("no signal", "no signal"),
        ("not synchronized", "not synchronized"),
    )
    Status = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="stopped")
    MacAddress = models.CharField('Mac Address', max_length=100, unique=True, null=True, blank =True)
    
    Available_CHOICES = (
        (True,"available"),
        (False,"not available")
    )
    Available = models.BooleanField('Available',choices=Available_CHOICES, default=True)
    Refresh_CHOICES = (
        (30,"30s"),
        (60,"1m"),
        (120,"2m"),
        (300,"5m"),
        (600,"10m"),
        (900,"15m"),
        (1800,"30m"),
    )
    Refresh = models.FloatField('Refresh', choices=Refresh_CHOICES,null=True, blank =True,default=120)

    objects = WellManager()
    class Meta:
        verbose_name = 'well'
        verbose_name_plural = 'wells'

    def __str__(self):
        #return '%s (%s)' % (self.PumpName,self.Available)
        return self.PumpName
        #return str(self.id) + '-' + self.PumpName

class tank(models.Model):
    id = models.BigAutoField(primary_key=True)
    DateCreate = models.DateTimeField(auto_now_add= True )
    TankName = models.CharField('Tank Name', max_length=100, unique=True)
    IdField = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    IdBattery = models.ForeignKey(Battery, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    IdGroup = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    Location = models.CharField('Location', max_length=100)
    InstallationDate = models.DateField(auto_now_add = False)
    VolumeFactor = models.FloatField('Volume Factor',null=True, blank =True)
    TankHeight = models.FloatField('Tank Height',null=True, blank =True)
    
    SupervisorUser = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)

    # Monitoring data
    Status_CHOICES = (
        ("stopped", "stopped"),
        ("running", "running"),
        ("low battery", "low battery"),
        ("no signal", "no signal"),
        ("not synchronized", "not synchronized"),
    )
    Status = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="stopped")

    Refresh_CHOICES = (
        (30,"30s"),
        (60,"1m"),
        (120,"2m"),
        (300,"5m"),
        (600,"10m"),
        (900,"15m"),
        (1800,"30m"),
    )
    Refresh = models.FloatField('Refresh', choices=Refresh_CHOICES,null=True, blank =True,default=120)

    class Meta:
        verbose_name = 'tank'
        verbose_name_plural = 'tanks'

    def __str__(self):
        return self.TankName