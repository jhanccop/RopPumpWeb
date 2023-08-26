from django.db import models
from django.conf import settings

from Apps.wells.models import well

from .managers import ProductionManager

# Create your models here.
class ProductionFluid(models.Model):

    PumpName = models.ForeignKey(well, on_delete=models.CASCADE, null=True)
    DateCreate = models.DateTimeField(auto_now_add = True, blank = True)

    UserAuthor = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    OilProd = models.FloatField('Oil Production', null=True, blank =True)
    WaterProd = models.FloatField('Water Production', null=True, blank =True)
    DateTest = models.DateField(auto_now_add=False, blank=True, null=True)
    #TubingPressure = models.FloatField('Tubing Pressure', null=True, blank =True)

    objects = ProductionManager()

    class Meta:
        verbose_name = 'Production'
        verbose_name_plural = 'All production'

    def __str__(self):
        #return '%s (%s)' % (self.PumpName,self.Available)
        return str(self.PumpName)