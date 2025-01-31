from django.db import models
from Apps.field.models import Field

from .managers import LocationManager

class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    DateCreated = models.DateTimeField(auto_now_add= True)
    LocationName = models.CharField('Location Name', max_length=100, unique=True, blank=True)
    Field = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False, blank=True)
    
    objects = LocationManager()
    
    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.LocationName