from django.db import models

class infoRequests(models.Model):
    id = models.BigAutoField(primary_key=True)
    DateCreate = models.DateTimeField(auto_now_add = True)
    Name = models.CharField('Nombre', max_length=100, unique=True, blank=True)
    LastName = models.CharField('Apellido', max_length=100, unique=True, blank=True)
    Email = models.CharField('Correo', max_length=100, unique=True, blank=True)
    Organization = models.CharField('Organización', max_length=100, unique=True, blank=True)

    MONFAUNA = "0"
    MONPLAGAS = "1"
    INDUSTRIA = "2"
    OTRO = "3"

    INTERES_CHOICES = (
        (MONFAUNA, 'Monitoreo de fauna'),
        (MONPLAGAS, 'Monitoreo de plagas'),
        (INDUSTRIA, 'Industria'),
        (OTRO, 'Otros'),
    )
    Interes = models.CharField('Interés', choices = INTERES_CHOICES,max_length=1100,blank =True,null=True)
    
    Message = models.TextField('Mensaje',  null=True, blank =True)

    class Meta:
        verbose_name = 'Contacto de interés'
        verbose_name_plural = 'Todos los contactos de interés'

    def __str__(self):
        return f"{self.Organization} {self.get_Interes_display()}"