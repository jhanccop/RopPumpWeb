import os

from django.db import models
from django.conf import settings

from .managers import CameraStationManager, CameraCaptureManager


class CameraStation(models.Model):
    id = models.BigAutoField(primary_key=True)

    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='cam_owner'
    )
    DateCreate = models.DateTimeField(auto_now_add=True)

    StationName = models.CharField('Station Name', max_length=100, unique=True)
    Description = models.TextField('Description', max_length=500, blank=True, null=True)

    Latitude = models.FloatField('Latitude', null=True, blank=True)
    Longitude = models.FloatField('Longitude', null=True, blank=True)
    Altitude = models.FloatField('Altitude (m)', null=True, blank=True)

    MacAddress = models.CharField('MAC Address', max_length=17, blank=True, null=True,
                                   help_text='e.g. AA:BB:CC:DD:EE:FF')

    # Schedule
    TurnOnTime  = models.TimeField('Turn On Time',  default='10:00')
    TurnOffTime = models.TimeField('Turn Off Time', default='17:00')

    # Detection parameters
    TIMESLEEP_CHOICES = (('5m', '5 minutes'), ('30m', '30 minutes'), ('1h', '1 hour'))
    TimeSleep   = models.CharField('Time Sleep', max_length=5, choices=TIMESLEEP_CHOICES, default='1h')

    TIMESLEEPC_CHOICES = ((5, '5 s'), (20, '20 s'), (30, '30 s'), (60, '60 s'))
    TimeSleepC  = models.PositiveSmallIntegerField('Capture Interval (s)', choices=TIMESLEEPC_CHOICES, default=30)
    Sensitivity = models.FloatField('Sensitivity (0–1)', default=0.6)

    # Available sensors
    HasTempHumidity = models.BooleanField('Temperature & Humidity Sensor', default=True)

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Maintenance', 'Maintenance'),
        ('Out of service', 'Out of service'),
    )
    Status = models.CharField('Status', max_length=50, choices=STATUS_CHOICES, default='Active')

    objects = CameraStationManager()

    class Meta:
        verbose_name = 'Camera Station'
        verbose_name_plural = 'Camera Stations'

    def __str__(self):
        return self.StationName


class CameraCapture(models.Model):
    id = models.BigAutoField(primary_key=True)

    Station = models.ForeignKey(
        CameraStation,
        on_delete=models.CASCADE,
        related_name='captures'
    )
    DateCapture = models.DateTimeField('Capture Date / Time')

    Image = models.ImageField(
        'Capture Image',
        upload_to='camera_captures/%Y/%m/',
        null=True, blank=True
    )

    Temperature = models.FloatField('Temperature (°C)', null=True, blank=True)
    Humidity = models.FloatField('Humidity (%)', null=True, blank=True)
    VoltageBattery = models.FloatField('Battery Voltage (V)', null=True, blank=True)
    MemFree = models.FloatField('Free Memory (KB)', null=True, blank=True)

    Notes = models.TextField('Notes', max_length=500, blank=True, null=True)

    objects = CameraCaptureManager()

    class Meta:
        verbose_name = 'Camera Capture'
        verbose_name_plural = 'Camera Captures'
        ordering = ['-DateCapture']

    def __str__(self):
        return f'{self.Station} — {self.DateCapture:%Y-%m-%d %H:%M}'

    def _delete_image_file(self, image_field):
        if image_field and image_field.name:
            path = os.path.join(settings.MEDIA_ROOT, image_field.name)
            if os.path.isfile(path):
                os.remove(path)

    def delete(self, *args, **kwargs):
        self._delete_image_file(self.Image)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = CameraCapture.objects.get(pk=self.pk)
                if old.Image and old.Image != self.Image:
                    self._delete_image_file(old.Image)
            except CameraCapture.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class CameraDeviceHealth(models.Model):
    """Periodic health report sent by the device (no image attached)."""
    Station = models.ForeignKey(
        CameraStation,
        on_delete=models.CASCADE,
        related_name='health_logs'
    )
    DateRecord = models.DateTimeField('Recorded At', auto_now_add=True)
    VoltageBattery = models.FloatField('Battery (V)', null=True, blank=True)
    MemFree = models.FloatField('Free Memory (KB)', null=True, blank=True)
    Temperature = models.FloatField('Temperature (°C)', null=True, blank=True)
    Humidity = models.FloatField('Humidity (%)', null=True, blank=True)

    class Meta:
        verbose_name = 'Device Health Log'
        verbose_name_plural = 'Device Health Logs'
        ordering = ['-DateRecord']

    def __str__(self):
        return f'{self.Station} — {self.DateRecord:%Y-%m-%d %H:%M}'


class SpeciesLabel(models.Model):
    ClassId = models.PositiveIntegerField('Class ID', unique=True)
    Name = models.CharField('Species Name', max_length=200, unique=True)
    Description = models.TextField('Description', blank=True, default='')

    class Meta:
        ordering = ['ClassId']
        verbose_name = 'Species / Class Label'
        verbose_name_plural = 'Species / Class Labels'

    def __str__(self):
        return f'{self.ClassId} — {self.Name}'


class CaptureDetection(models.Model):
    Capture = models.ForeignKey(
        CameraCapture,
        on_delete=models.CASCADE,
        related_name='detections',
    )
    Species = models.CharField('Species / Class', max_length=200)
    Count = models.PositiveIntegerField('Count', default=1)

    class Meta:
        verbose_name = 'Detection'
        verbose_name_plural = 'Detections'

    def __str__(self):
        return f'{self.Species} × {self.Count}'

