from django.db import models
from Apps.company.models import Company

from .managers import FieldManager

# Create your models here.
class Field(models.Model):
    id = models.BigAutoField(primary_key=True)
    DateCreated = models.DateTimeField(auto_now_add= True)
    FieldName = models.CharField('Field Name', max_length=100, unique=True, blank=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False, blank=True)
    #LocationState = models.CharField('Location State', max_length=100)
    #LocationCounty = models.CharField('Location County', max_length=100)

    objects = FieldManager()
    
    class Meta:
        verbose_name = 'Field'
        verbose_name_plural = 'Fields'

    def __str__(self):
        return self.FieldName

    #def __str__(self):
    #    return f'{self.id}: {self.FieldName}'