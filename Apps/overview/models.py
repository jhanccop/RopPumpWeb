from django.db import models
from django.conf import settings

from Apps.wells.models import well
from multiselectfield import MultiSelectField

from .managers import RPDataManager

class RodPumpData(models.Model):
    PumpName = models.ForeignKey(well, on_delete=models.CASCADE, null=True, blank=True)

    DateCreate = models.DateTimeField(auto_now_add= True, blank =True)
    SurfaceLoad = models.TextField('Surf Load',  null=True, blank =True)
    SurfacePosition = models.TextField('Surf Position', null=True, blank =True)
    DownLoad = models.TextField('Down Load',  null=True, blank =True)
    DownPosition = models.TextField('Down Position', null=True, blank =True)
    RunTime =  models.FloatField('Run Time', null=True, blank =True)
    RawAcceleration = models.TextField('RawAcceleration', null=True, blank =True)

    TubingPressure = models.FloatField('Tubing Pressure', null=True, blank =True)
    CasingPressure = models.FloatField('Casing Pressure', null=True, blank =True)
    SPM = models.FloatField('SPM', null=True, blank =True)
    Status = models.CharField('Status', max_length=20,null=True, blank =True)

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
    PumpFill = models.FloatField('Pump Fill', null=True, blank =True)

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
        #return '%s (%s)' % (self.PumpName,self.Available)
        return str(self.PumpName)
        #return str(self.id) + '-' + self.PumpName
