from django.db import models
from django.conf import settings

from django.db.models.signals import (
    post_save
)
from django.dispatch import receiver

from Apps.equipment.models import Tank, RodPumpWell, Environmental, VisualSamplingPoint
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
    
class CamVidDevice(models.Model):
    id = models.BigAutoField(primary_key=True)

    IdVisualSamplingPoint = models.ForeignKey(VisualSamplingPoint, on_delete=models.CASCADE, unique=False,blank=True,null=True)

    # General information
    Owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    DateCreate = models.DateTimeField(auto_now_add= True )
    DeviceName = models.CharField('Device Name', max_length=50, unique=True)
    DeviceMacAddress = models.CharField('Mac Address', max_length=50, unique=True)

    TimeStart = models.TimeField("On time" ,null=True, blank=True )
    TimeEnd = models.TimeField("Off time",null=True, blank=True )
    
    M2 = 2
    M5 = 5
    M30 = 30
    M60 = 60
    M120 = 120

    SleepTime_CHOICES = (
        (M2,"2 m"),
        (M5,"5 m"),
        (M30,"30 m"),
        (M60,"1 h"),
        (M120,"2 h"),
    )
    SleepTime = models.IntegerField('Sleep Time', choices=SleepTime_CHOICES,null=True, blank =True,default=60)

    is_continous = models.BooleanField("continuous?", default = False)

    S10 = 10
    S20 = 20
    S60 = 60
    refresh_CHOICES = (
        (S10,"10 s"),
        (S20,"20 s"),
        (S60,"60 s"),
    )
    refresh = models.IntegerField('Sampling Rate', choices=refresh_CHOICES,null = True, blank =True,default = 10)
    saveImage = models.BooleanField("save Image?", default = False)
    runningNN = models.BooleanField("running NN?", default = False)

    objects = EnvironmentalDeviceManager()
    class Meta:
        verbose_name = 'Cam video device'
        verbose_name_plural = 'Cam video devices'

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

"""    
@receiver(post_save, sender=CamVidDevice)
def send_update_setting(sender, instance,**kwargs):
    import random
    import paho.mqtt.client as mqtt_client
    import json
    import time
    from datetime import datetime, timedelta

    broker = 'broker.hivemq.com' #'broker.emqx.io'
    port = 1883

    topicPub = "jhpOandG/settings"
    client_id = f'publish-{random.randint(0, 1000)}'

    def connect_mqtt():
        def on_connect(client, userdata, flags, rc, props=None):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        #client = mqtt_client.Client(client_id, userdata="glertps")

        client.on_connect = on_connect
        client.connect(broker, port)
        return client
    
    client = connect_mqtt()

    dtNow = datetime.now() - timedelta(hours=5)
    print(dtNow)
    #dtNow = datetime.now()
    timeNow = dtNow.time()
    timeStart = instance.TimeStart
    timeEnd = instance.TimeEnd

    status = False
    if timeNow >= timeStart and timeNow <= timeEnd:
        status = True
    
    msg = {
        "name":instance.DeviceName,
        "timesleep":instance.SleepTime,
        "status":status,
        "continuous":instance.is_continous,
        "refresh":instance.refresh
    }

    msg = json.dumps(msg)

    client.loop_start()

    time.sleep(2)

    result,x = client.publish(topicPub, msg)

    client.loop_stop()

"""    
    