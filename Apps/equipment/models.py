from model_utils.models import TimeStampedModel

from django.db import models
from django.conf import settings

from Apps.field.models import Field
from Apps.batteries.models import Battery
from Apps.groups.models import Group

from .managers import TankManager, WellManager, EnvironmentalManager

class RodPumpWell(models.Model):
    id = models.BigAutoField(primary_key=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL,related_name="RP_owner")
    DateCreate = models.DateTimeField(auto_now_add= True )
    WellName = models.CharField('Well Name', max_length=50, unique=True)
    FieldName = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    BatteryName = models.ForeignKey(Battery, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    GroupName = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    LatLocation = models.FloatField('Latitude', null=True, blank =True)
    LonLocation = models.FloatField('Longitude', null=True, blank =True)
    InstallationDate = models.DateField(auto_now_add = False)
    InstallationComment = models.TextField('Installation Comment', max_length=500)
    SupervisorUser = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)  

    # DOWNHOLE DATA
    PumpIntake = models.FloatField('Pump Intake', null=True, blank =True)
    MeasuredDepth = models.FloatField('Measured Depth', null=True, blank =True)
    PlungerDiameter = models.FloatField('Plunger Diameter', null=True, blank =True)
    TrueVerticalDepth = models.FloatField('True Vertical Depth', null=True, blank =True)
    TotalRodLength = models.FloatField('Total Rod Length', null=True, blank =True)
    TotalRodWeight = models.FloatField('Total Rod Weight', null=True, blank =True)
    
    # SURFACE DATA
    StrokeLength = models.FloatField('Stroke Length', null=True, blank =True)
    TYPE_MOTOR_CHOICES = (
        ("Electric", "Electric"),
        ("Gas", "Gas"),
    )
    EngineType = models.CharField('Engine Type', max_length=50, choices=TYPE_MOTOR_CHOICES, default="Gas")
    PolishedRodDiameter = models.FloatField('Polished Rod Diameter', null=True, blank =True)
    EngineBrand = models.CharField('Engine Brand', max_length=50, unique=False)

    # PRODUCTION CONFIG
    ProdTime = models.FloatField('Production Time', null=True, blank =True)
    RestTime = models.FloatField('Rest Time', null=True, blank =True)
    # Monitoring data
    Status_CHOICES = (
        ("Out of service", "Out of service"),
        ("Maintenance", "Maintenance"),
        ("Normal running", "Mormal running"),
        ("Testing", "Testing"),
        ("Not assigned", "Not assigned"),
    )
    Status = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="Normal running")
    #IdAnalyzer = models.ForeignKey(WellAnalyzerDevice, on_delete=models.CASCADE, unique=True,blank=True,null=True)
    
    objects = WellManager()

    class Meta:
        verbose_name = 'Rod Pump Well'
        verbose_name_plural = 'Rod Pump Wells'

    def __str__(self):
        return self.WellName

class Tank(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL,related_name="Tank_owner")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    TankName = models.CharField('Tank Name', max_length=100, unique=True)
    FieldName = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False,blank=True)
    BatteryName = models.ForeignKey(Battery, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    GroupName = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    LatLocation = models.FloatField('Latitude', null=True, blank =True)
    LonLocation = models.FloatField('Longitude', null=True, blank =True)
    SupervisorUser = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)  
    
    # TANK DATA
    TankHeight = models.FloatField('Tank Height',null=True, blank =True)
    TankFactor = models.FloatField('Tank Factor',null=True, blank =True)

    WellsAssigned = models.ManyToManyField(RodPumpWell)
   
    # Monitoring data
    Status_CHOICES = (
        ("Out of service", "Out of service"),
        ("Maintenance", "Maintenance"),
        ("Normal running", "Normal running"),
        ("Testing", "Testing"),
        ("Not assigned", "Not assigned"),
    )
    Status = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="Normal running")
    #IdAnalyzer = models.ForeignKey(TankDevice, on_delete=models.CASCADE, unique=True,blank=True,null=True)
    
    objects = TankManager()
    class Meta:
        verbose_name = 'Tank'
        verbose_name_plural = 'Tanks'
        #unique_together = ('TankName',)

    def __str__(self):
        return self.TankName
    
class Environmental(models.Model):
    id = models.BigAutoField(primary_key=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL,related_name="Env_owner")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    EnvironmentalName = models.CharField('Environmental Name', max_length=100, unique=True)
    #FieldName = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False,blank=True, null=True)
    #BatteryName = models.ForeignKey(Battery, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    GroupName = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    LatLocation = models.FloatField('Latitude', null=True, blank =True)
    LonLocation = models.FloatField('Longitude', null=True, blank =True)
    SupervisorUser = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)  
   
    # Monitoring data
    Status_CHOICES = (
        ("Out of service", "Out of service"),
        ("Maintenance", "Maintenance"),
        ("Normal running", "Normal running"),
        ("Testing", "Testing"),
        ("Not assigned", "Not assigned"),
    )
    Status = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="normal running")
       
    objects = EnvironmentalManager()
    class Meta:
        verbose_name = 'Environment'
        verbose_name_plural = 'Environmental sesnors'
        #unique_together = ('TankName',)

    def __str__(self):
        return self.EnvironmentalName

""" 
class WellsTanks(models.Model):
    Tanks = models.ForeignKey(Tank, on_delete=models.CASCADE,blank=True,null=True)
    Wells = models.ForeignKey(RodPumpWell, on_delete=models.CASCADE,blank=True,null=True)

    Describe = models.CharField('Describe', max_length=100, blank=True)

    class meta:
        db_table = 'rodpumpwell_rodpumpwell_wells'
        verbose_name = 'tank in well'
        verbose_name_plural = 'tanks in wells'
    
    def __str__(self) -> str:
        return self.Tanks.TankName + " - " + self.Wells.WellName
"""