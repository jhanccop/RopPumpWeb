from django.db import models

# Create your models here.

from .managers import CompanyManager
class Company(models.Model):

    # General information
    DateCreate = models.DateTimeField(auto_now_add=True)
    CompanyName = models.CharField('Company Name', max_length=100, unique=True)
    LocationState = models.CharField('Location State', max_length=100)
    LocationCounty = models.CharField('Location County', max_length=100)

    objects = CompanyManager()

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.CompanyName
        #return str(self.CompanyName)