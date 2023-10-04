from django.db import models
from django.conf import settings

from Apps.wells.models import well

from .managers import SettingManager

# Create your models here.
class setting(models.Model):

    DateCreated = models.DateTimeField(auto_now_add= True)
    DeviceName = models.CharField('Device Name', max_length=100, unique=True, null=True, blank =True)
    PumpName = models.ForeignKey(well, on_delete=models.CASCADE, null=True, blank=True)
  
    # Operational information
    Available_CHOICES = (
        (True,"available"),
        (False,"not available")
    )
    Available = models.BooleanField('Available',choices=Available_CHOICES, default=True)
    Types_CHOICES = (
        ("Rod Pump Analyzer","Rod Pump Analyzer"),
        ("Tank Level Meter","Tank Level Meter")
    )
    DeviceType = models.CharField('Device Type', max_length=50, choices=Types_CHOICES, default="Rod Pump Analyzer")
    MacAddress = models.CharField('Mac Address', max_length=100, unique=True, null=True, blank =True)
    IpAddress = models.CharField('Ip Address', max_length=100, unique=True)
    Status_CHOICES = (
        ("stopped", "stopped"),
        ("running", "running"),
        ("low battery", "low battery"),
        ("no signal", "no signal"),
    )
    Status = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="stopped")
    TimeOn = models.FloatField('Time On',null=True, blank =True)
    TimeOff = models.FloatField('Time Off',null=True, blank =True)
    ThresholdAlert1 = models.FloatField('Threshold Alert 1',null=True, blank =True)
    ThresholdAlert2 = models.FloatField('Threshold Alert 2',null=True, blank =True)
    ThresholdStop = models.FloatField('Threshold Stop',null=True, blank =True)
    TankHeight = models.FloatField('Tank Height',null=True, blank =True)
    TankFactor = models.FloatField('Tank Factor',null=True, blank =True)

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

    objects = SettingManager()

    class Meta:
        verbose_name = 'setting'
        verbose_name_plural = 'all settings'

    def __str__(self):
        #return '%s (%s)' % (self.PumpName,self.Available)
        return str(self.PumpName)
        #return str(self.id) + '-' + self.PumpName