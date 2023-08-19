from django.db import models

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager, models.Manager):

    def _create_user(self, UserName, Email, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            UserName = UserName,
            Email = Email,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    #def create_user(self, username, password=None,  **extra_fields):

    def create_user(self, UserName, Email, password=None, **extra_fields):
        return self._create_user(UserName, Email, password, False, False, **extra_fields)

    def create_superuser(self, UserName, Email, password=None, **extra_fields):
        return self._create_user(UserName, Email, password, True, True, **extra_fields)

    def get_company_id(self, UserName):
        result = self.filter(
                UserName=UserName
            ).values("CompanyName")
        #print("*******", result)
        return result
