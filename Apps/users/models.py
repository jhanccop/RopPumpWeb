from email.policy import default
#from statistics import mode
from django.db import models

from Apps.company.models import Company
from .managers import UserManager

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    UserName = models.CharField(max_length=20, unique=True)
    Email = models.EmailField()
    Name = models.CharField(max_length=30, blank=True)
    LastName = models.CharField(max_length=30,blank=True)
    #CompanyName = models.CharField(max_length=30)
    CompanyName = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,related_name='company_user')
   
    is_staff = models.BooleanField(default=False)
    #is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "UserName"

    REQUIRED_FIELDS = ["Email",]

    objects = UserManager()

    def get_short_name(self):
        return self.UserName

    def get_full_name(self):
        return self.UserName + ' ' + self.LastName