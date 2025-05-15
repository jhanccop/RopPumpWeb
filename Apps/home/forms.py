# forms.py
from django import forms
from .models import infoRequests
from django.core.exceptions import ValidationError
import re

class infoRequestsForm(forms.ModelForm):
    class Meta:
        model = infoRequests
        fields = ['Name', 'LastName', 'Email', 'Organization', 'Interes', 'Message']
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'input-group-field form-control', 'placeholder': 'Nombre'}),
            'LastName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'Organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organización'}),
            'Interes': forms.Select(attrs={'class': 'form-control'}),
            'Message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mensaje', 'rows': 4}),
        }
        
    def clean_Email(self):
        """
        Validación personalizada para el email
        """
        Email = self.cleaned_data.get('Email')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, Email):
            raise ValidationError("Ingrese un correo electrónico válido.")
        
        return Email
    
    def clean_Name(self):
        """
        Validación para el nombre
        """
        Name = self.cleaned_data.get('Name')
        
        # Validación básica de nombre
        if len(Name) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        
        # Validación de caracteres permitidos
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', Name):
            raise ValidationError("El nombre contiene caracteres no válidos.")
        
        return Name
    
    def clean_Message(self):
        """
        Validación para el mensaje
        """
        Message = self.cleaned_data.get('Message')
        
        # Validación de longitud del mensaje
        if Message and len(Message) > 500:
            raise ValidationError("El mensaje no puede exceder los 500 caracteres.")
        
        return Message