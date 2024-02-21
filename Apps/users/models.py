from email.policy import default
#from statistics import mode
from django.db import models

from Apps.company.models import Company
from .managers import UserManager

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    Name = models.CharField(max_length=30, blank=True)
    LastName = models.CharField(max_length=30,blank=True)
    UserName = models.CharField(max_length=20, unique=True)
    #CompanyName = models.CharField(max_length=30)
    CompanyId = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,related_name='company_user')
    Email = models.EmailField()
    is_staff = models.BooleanField(default=False)
    #is_superuser = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ("Manager", "Manager"),
        ("Worker", "Worker"),
    )
    Role = models.CharField('Role', max_length=10, choices=ROLE_CHOICES, default="Worker")
    
    USERNAME_FIELD = "UserName"

    REQUIRED_FIELDS = ["Email",]

    objects = UserManager()

    def get_short_name(self):
        return self.UserName

    def get_full_name(self):
        return self.UserName + ' ' + self.LastName