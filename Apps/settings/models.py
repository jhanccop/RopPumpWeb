from django.db import models

from Apps.wells.models import well

# Create your models here.
class setting(models.Model):

    DateCreated = models.DateTimeField(auto_now_add= True)
    PumpName = models.OneToOneField(well, on_delete=models.CASCADE,null=True, blank=False)
  
    # Operational information
    Available = models.BooleanField('Available',default=True)
    IpAddress = models.CharField('Ip Address', max_length=100, unique=True)
    Refresh = models.FloatField('Refresh Time',null=True, blank =True)