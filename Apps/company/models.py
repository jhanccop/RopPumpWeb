from django.db import models

from .managers import CompanyManager
class Company(models.Model):
    OILGAS = "0"
    AGRICULTURAL = "1"
    OTHER = "9"

    TYPE_CHOICES = [
        (OILGAS, "Oil Production"),
        (AGRICULTURAL, "Agricultural"),
        (OTHER, "Other"),
    ]

    id = models.BigAutoField(primary_key=True)
    # General information
    CompanyName = models.CharField('Company Name', max_length=100, unique=True)
    LocationState = models.CharField('Location State', max_length=100)
    LocationCounty = models.CharField('Location County', max_length=100)
    DateCreate = models.DateTimeField(auto_now_add=True)

    CompanyType = models.CharField('Role',max_length=2, choices = TYPE_CHOICES, default="9", blank=True, null=True)
    
    objects = CompanyManager()

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.CompanyName