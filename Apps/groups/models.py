from django.db import models
from Apps.company.models import Company

# Create your models here.
from .managers import GroupManager

# Create your models here.
class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    DateCreated = models.DateTimeField(auto_now_add= True)
    GroupName = models.CharField('Group Name', max_length=100,unique=True,blank=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False,blank=True)

    objects = GroupManager()
    
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.GroupName