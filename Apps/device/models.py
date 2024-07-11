from django.db import models
from django.conf import settings

from Apps.equipment.models import Tank, RodPumpWell, Environmental
from .managers import TankDeviceManager, EnvironmentalDeviceManager, AnalyzerDeviceManager

class TankDevice(models.Model):
    id = models.BigAutoField(primary_key=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    DateCreate = models.DateTimeField(auto_now_add= True )
    DeviceName = models.CharField('Device Name', max_length=50, unique=True)
    DeviceMacAddress = models.CharField('Device Mac Address', max_length=50, unique=True)

    # Monitoring data
    Status_CHOICES = (
        ("Normal running", "Normal running"),
        ("Low battery", "Low battery"),
        ("No signal", "No signal"),
    )
    DeviceStatus = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="normal running")
    Refresh_CHOICES = (
        (1800,"0.5h"),
        (3600,"1h"),
        (7200,"2h"),
    )
    SamplingRate = models.IntegerField('Sampling Rate', choices=Refresh_CHOICES,null=True, blank =True,default=1800)
    IdTank = models.ForeignKey(Tank, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    
    objects = TankDeviceManager()
    class Meta:
        verbose_name = 'tank device'
        verbose_name_plural = 'tank devices'

    def __str__(self):
        return self.DeviceName
    
class EnvironmentalDevice(models.Model):
    id = models.BigAutoField(primary_key=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    DateCreate = models.DateTimeField(auto_now_add= True )
    DeviceName = models.CharField('Device Name', max_length=50, unique=True)
    DeviceMacAddress = models.CharField('Device Mac Address', max_length=50, unique=True)

    # Monitoring data
    Status_CHOICES = (
        ("Normal running", "Normal running"),
        ("Low battery", "Low battery"),
        ("No signal", "No signal"),
    )
    DeviceStatus = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="normal running")
    Refresh_CHOICES = (
        (1800,"0.5h"),
        (3600,"1h"),
        (7200,"2h"),
    )
    SamplingRate = models.IntegerField('Sampling Rate', choices=Refresh_CHOICES,null=True, blank =True,default=1800)
    IdEnvironmental  = models.ForeignKey(Environmental, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    
    objects = EnvironmentalDeviceManager()
    class Meta:
        verbose_name = 'Environmental device'
        verbose_name_plural = 'Environmental devices'

    def __str__(self):
        return self.DeviceName

class WellAnalyzerDevice(models.Model):
    id = models.BigAutoField(primary_key=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    DateCreate = models.DateTimeField(auto_now_add= True )
    DeviceName = models.CharField('Device Name', max_length=50, unique=True)
    DeviceMacAddress = models.CharField('Device Mac Address', max_length=50, unique=True)

    # Monitoring data
    Status_CHOICES = (
        ("normal running", "normal running"),
        ("low battery", "low battery"),
        ("no signal", "no signal"),
    )
    DeviceStatus = models.CharField('Status', max_length=50, choices=Status_CHOICES, default="normal running")
    Refresh_CHOICES = (
        (1800,"0.5h"),
        (3600,"1h"),
        (7200,"2h"),
    )
    SamplingRate = models.IntegerField('Sampling Rate', choices=Refresh_CHOICES,null=True, blank =True,default=120)
    IdRodPumpWell = models.ForeignKey(RodPumpWell, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    
    objects = AnalyzerDeviceManager()
    class Meta:
        verbose_name = 'Well Analyzer device'
        verbose_name_plural = 'Well Analyzer devices'

    def __str__(self):
        return self.DeviceName
