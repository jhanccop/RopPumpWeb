from django import forms
from .models import SecurityDevice, Sensor, SENSOR_KEYS, CATEGORY_CHOICES


class SecurityDeviceForm(forms.ModelForm):
    class Meta:
        model  = SecurityDevice
        fields = ['Name', 'Description', 'MacAddress', 'Location',
                  'MqttBroker', 'MqttPort', 'MqttTopic',
                  'Status', 'Owner']
        widgets = {
            'Name':        forms.TextInput(attrs={'class': 'form-control'}),
            'Description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'MacAddress':  forms.TextInput(attrs={'class': 'form-control'}),
            'Location':    forms.TextInput(attrs={'class': 'form-control'}),
            'MqttBroker':  forms.TextInput(attrs={'class': 'form-control'}),
            'MqttPort':    forms.NumberInput(attrs={'class': 'form-control'}),
            'MqttTopic':   forms.TextInput(attrs={'class': 'form-control'}),
            'Status':      forms.Select(attrs={'class': 'form-control'}),
            'Owner':       forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'Name':        'Nombre del dispositivo',
            'MacAddress':  'MAC Address',
            'Location':    'Ubicación / Instalación',
            'MqttBroker':  'Broker MQTT',
            'MqttPort':    'Puerto MQTT',
            'MqttTopic':   'Topic de escucha',
            'Status':      'Estado',
            'Owner':       'Responsable',
        }


class SensorForm(forms.ModelForm):
    class Meta:
        model  = Sensor
        fields = ['Enabled', 'Category']
        widgets = {
            'Enabled':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Category': forms.Select(attrs={'class': 'form-select form-select-sm'},
                                     choices=CATEGORY_CHOICES),
        }
