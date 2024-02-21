from django.db import models

class EngineType(models.Model):
    id = models.BigAutoField(primary_key=True)
    ENGINE_CHOICES = (
        ("Electric", "Electric"),
        ("Gas", "Gas"),
    )
    EngineType = models.CharField('Engine Type', max_length=20, choices=ENGINE_CHOICES, default="Gas")
    EnginePower = models.FloatField('Engine Power', null=True, blank =True)
    EngineBrand = models.CharField('Engine Brand', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Engine Type'
        verbose_name_plural = 'Engine Types'

    def __str__(self):
        return self.EngineType