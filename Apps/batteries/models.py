from django.db import models
from Apps.company.models import Company

# Create your models here.
from .managers import BatteryManager

# Create your models here.
class Battery(models.Model):
    DateCreated = models.DateTimeField(auto_now_add= True)
    BatteryName = models.CharField('Battery Name', max_length=100,unique=True,blank=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False,blank=True)

    objects = BatteryManager()
    
    class Meta:
        verbose_name = 'Battery'
        verbose_name_plural = 'Batteries'

    def __str__(self):
        #return '%s (%s)' % (self.PumpName,self.Available)
        return self.BatteryName
        #return str(self.id)
