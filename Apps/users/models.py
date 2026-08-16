from django.db import models
from Apps.company.models import Company
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class Application(models.Model):
    CODE_CHOICES = [
        ('transformadores', 'Transformadores'),
        ('fauna', 'Fauna'),
        ('oilfield', 'Oilfield'),
        ('seguridad', 'Seguridad'),
    ]
    Code = models.CharField('Código', max_length=50, unique=True, choices=CODE_CHOICES)
    Name = models.CharField('Nombre', max_length=100)
    Description = models.TextField('Descripción', blank=True)
    Icon = models.CharField('Ícono FA', max_length=60, blank=True, default='fas fa-th')
    DashboardUrl = models.CharField('URL Dashboard', max_length=100, blank=True)
    IsActive = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Aplicación'
        verbose_name_plural = 'Aplicaciones'

    def __str__(self):
        return self.Name


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    Name = models.CharField(max_length=30, blank=True)
    LastName = models.CharField(max_length=30, blank=True)
    UserName = models.CharField(max_length=20, unique=True)
    CompanyId = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, related_name='company_user')
    Email = models.EmailField()
    is_staff = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ("superadmin", "Super Admin"),
        ("admin", "Administrador"),
        ("operator", "Operador"),
    ]
    Role = models.CharField('Role', max_length=10, choices=ROLE_CHOICES, default="operator")

    Applications = models.ManyToManyField(
        Application,
        blank=True,
        related_name='users',
        verbose_name='Aplicaciones habilitadas',
    )
    IsActive = models.BooleanField('Activo', default=True)

    USERNAME_FIELD = "UserName"
    REQUIRED_FIELDS = ["Email"]

    objects = UserManager()

    def get_short_name(self):
        return self.UserName

    def get_full_name(self):
        return self.UserName + ' ' + self.LastName

    @property
    def is_superadmin(self):
        return self.Role == 'superadmin' or self.is_superuser

    @property
    def is_admin(self):
        return self.Role in ('superadmin', 'admin') or self.is_superuser

    def has_app_access(self, app_code):
        if self.is_superadmin:
            return True
        return self.Applications.filter(Code=app_code, IsActive=True).exists()

    def get_first_app_url(self):
        """
        Return the dashboard URL based on:
        1. For superadmins → admin panel
        2. For admins → admin panel of their primary app
        3. For operators → dashboard of their first enabled application

        Priority order respects company type if set:
          Oil company  → oilfield first
          Other        → order of assigned apps
        """
        # Admins go to admin panel first
        if self.is_admin:
            return '/admin-panel/'

        # Operators: go directly to their first allowed app
        apps = self.Applications.filter(IsActive=True).order_by('id')

        # If company has a preferred type, sort accordingly
        company = self.CompanyId
        if company and hasattr(company, 'CompanyType'):
            ctype = company.CompanyType
            # Oil production → oilfield first
            if ctype == '0':
                preferred = ['oilfield', 'transformadores', 'fauna', 'seguridad']
            # Agricultural → fauna first
            elif ctype == '1':
                preferred = ['fauna', 'oilfield', 'transformadores', 'seguridad']
            else:
                preferred = ['transformadores', 'oilfield', 'fauna', 'seguridad']

            for code in preferred:
                app = apps.filter(Code=code).first()
                if app and app.DashboardUrl:
                    return app.DashboardUrl

        # Fallback: first app in list
        app = apps.first()
        if app and app.DashboardUrl:
            return app.DashboardUrl

        return '/'
