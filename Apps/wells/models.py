from wsgiref.handlers import format_date_time
from django.db import models
from django.conf import settings

from Apps.field.models import Field
from Apps.batteries.models import Battery
from Apps.groups.models import Group

from .managers import WellManager

class well(models.Model):
    id = models.BigAutoField(primary_key=True)
    # General information
    DateCreate = models.DateTimeField(auto_now_add= True )
    PumpName = models.CharField('Pump Name', max_length=100, unique=True)
    #Company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False)
    FieldName = models.ForeignKey(Field, on_delete=models.CASCADE, unique=False,blank=True)
    BatteryName = models.ForeignKey(Battery, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    GroupName = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False,blank=True,null=True)
    Location = models.CharField('Location', max_length=100)
    UserAuthor = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    InstallationDate = models.DateField(auto_now_add = False)
    InstallationComment = models.TextField('Installation Comment', max_length=500)
    DesignStatus = models.IntegerField('Design Status', null=True, blank=True)

    # SURFACE DATA
    StrokeLength = models.FloatField('Stroke Length', null=True, blank =True)
    TYPE_MOTOR_CHOICES = (
        ("Electric", "Electric"),
        ("Gas", "Gas"),
    )
    MotorType = models.CharField('Motor Type', max_length=50, choices=TYPE_MOTOR_CHOICES, default="Gas")
    PolishedRodDiameter = models.FloatField('Polished Rod Diameter', null=True, blank =True)
    
    # DOWN DATA
    PumpIntake = models.FloatField('Pump Intake', null=True, blank =True)
    PlungerDiameter = models.FloatField('Plunger Diameter', null=True, blank =True)
    TrueVerticalDepth = models.FloatField('True Vertical Depth', null=True, blank =True)
    TotalRodLength = models.FloatField('Total Rod Length', null=True, blank =True)
    TotalRodWeight = models.FloatField('Total Rod Weight', null=True, blank =True)
    
    # type well
    TYPE_CHOICES = (
        ("Sucker Rod Pump", "Sucker Rod Pump"),
        ("Electrical Submersible Pump", "Electrical Submersible Pump"),
    )
    PumpType = models.CharField('Pump Type', max_length=50, choices=TYPE_CHOICES, default="Sucker Rod Pump")

    objects = WellManager()
    class Meta:
        verbose_name = 'well'
        verbose_name_plural = 'wells'

    def __str__(self):
        #return '%s (%s)' % (self.PumpName,self.Available)
        return self.PumpName
        #return str(self.id) + '-' + self.PumpName