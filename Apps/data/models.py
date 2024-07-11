from django.db import models

from Apps.device.models import TankDevice, WellAnalyzerDevice, EnvironmentalDevice
from multiselectfield import MultiSelectField

from .managers import RPDataManager, TankDataManager, EnvironmentalDataManager

# Create your models here.
class RodPumpData(models.Model):
    id = models.BigAutoField(primary_key=True)

    IdDevice = models.ForeignKey(WellAnalyzerDevice, on_delete=models.CASCADE, null=True, blank=True)
    DateCreate = models.DateTimeField(auto_now_add= True, blank =True)

    RawSurfaceLoad = models.TextField('Raw Surf Load',  null=True, blank =True)
    RawSurfacePosition = models.TextField('Raw Surf Position', null=True, blank =True)
    SurfaceLoad = models.TextField('Surf Load',  null=True, blank =True)
    SurfacePosition = models.TextField('Surf Position', null=True, blank =True)
    DownLoad = models.TextField('Down Load',  null=True, blank =True)
    DownPosition = models.TextField('Down Position', null=True, blank =True)
    RawAcceleration = models.TextField('RawAcceleration', null=True, blank =True)

    RunTime =  models.FloatField('Run Time', null=True, blank =True)
    SPM = models.FloatField('SPM', null=True, blank =True)
    Production = models.FloatField('Production', null=True, blank =True)

    DIAGNOSIS_CHOICES = (
        ('None', 'None'),
        ('Full pump', 'Full pump'),
        ('Leak travel valve', 'Leak travel valve'),
        ('Leak standing valve', 'Leak standing valve'),
        ('Worn pump barrel', 'Worn pump barrel'),
        ('Light fluid stroke', 'Light fluid stroke'),
        ('Medium fluid stroke', 'Medium fluid stroke'),
        ('Severe fluid stroke', 'Severe fluid stroke'),
        ('Gas interference', 'Gas interference'),
        ('Shock of pump up', 'Shock of pump up'),
        ('Shock of pump down', 'Shock of pump down'),
        ('Recovering level', 'Recovering level'),
        ("Rods broken","Rods broken")
    )
    
    Diagnosis = MultiSelectField("Diagnosis", choices = DIAGNOSIS_CHOICES,max_choices=3,max_length=100,blank =True,null=True)
    PumpFillage = models.FloatField('Pump Fillage', null=True, blank =True)

    STATUS_CHOICES = (
        ('Normal running', 'Normal running'),
        ('Stopped unit', 'Stopped unit'),
    )
    Status = models.CharField('Status', choices = STATUS_CHOICES,max_length=100,blank =True,null=True)
    
    Diagnosis = MultiSelectField("Diagnosis", choices = DIAGNOSIS_CHOICES,max_choices=3,max_length=100,blank =True,null=True)

    RECOMENDATION_CHOICES = (
        ('Good work area', 'Good work area'),
        ('Schedule to workover', 'Schedule to workover'),
        ('Unit re-spacing', 'Unit re-spacing'),
        ('Reduce strokes per minute', 'Reduce strokes per minute'),
        ('Stop pump unit', 'Stop pump unit'),
    )
    
    Recomendation = MultiSelectField("Recomendation", choices = RECOMENDATION_CHOICES,max_choices=3,max_length=100,blank =True,null=True)
    
    objects = RPDataManager()
    class Meta:
        verbose_name = 'Socker Rod Pump Data'
        verbose_name_plural = 'All Socker Rod Pump Data'

    def __str__(self):
        return str(self.IdDevice)

class TankData(models.Model):
    id = models.BigAutoField(primary_key=True)

    IdDevice = models.ForeignKey(TankDevice, on_delete=models.CASCADE, null=True, blank=True)
    DateCreate = models.DateTimeField(auto_now_add = True)
    Level = models.FloatField('Oil Level', null=True, blank =True)
    Temperature = models.FloatField('Temperature', null=True, blank =True)
    
    STATUS_CHOICES = (
        ('Normal running', 'Normal running'),
        ('Stopped', 'Stopped'),
    )
    Status = models.CharField('Status', choices = STATUS_CHOICES,max_length=100,blank =True,null=True)
     
    objects = TankDataManager()

    class Meta:
        verbose_name = 'Tank Data'
        verbose_name_plural = 'All Tank Data'

    def __str__(self):
        return str(self.IdDevice)
    
class EnvironmentalData(models.Model):
    id = models.BigAutoField(primary_key=True)

    IdDevice = models.ForeignKey(EnvironmentalDevice, on_delete=models.CASCADE, null=True, blank=True)
    DateCreate = models.DateTimeField(auto_now_add = True)
    Humidity1 = models.FloatField('Humidity 1', null=True, blank =True)
    Temperature1 = models.FloatField('Temperature 1', null=True, blank =True)
    AtmosphericPressure1 = models.FloatField('Atmospheric Pressure 1', null=True, blank =True)

    Humidity2 = models.FloatField('Humidity 2', null=True, blank =True)
    Temperature2 = models.FloatField('Temperature 2', null=True, blank =True)
    AtmosphericPressure2 = models.FloatField('Atmospheric Pressure 2', null=True, blank =True)
    
    STATUS_CHOICES = (
        ('Normal running', 'Normal running'),
        ('Stopped', 'Stopped'),
    )
    Status = models.CharField('Status', choices = STATUS_CHOICES,max_length=100,blank =True,null=True)
     
    objects = EnvironmentalDataManager()

    class Meta:
        verbose_name = 'Environmental Data'
        verbose_name_plural = 'All Environmental Data'

    def __str__(self):
        return str(self.IdDevice)
