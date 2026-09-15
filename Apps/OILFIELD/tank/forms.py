from django import forms
from .models import TankStation


class TankStationForm(forms.ModelForm):
    class Meta:
        model  = TankStation
        fields = [
            'Name', 'Description', 'MacAddress', 'Tank',
            'SensorType', 'SamplingRate',
            'MqttBroker', 'MqttPort',
            'Status', 'Owner',
        ]
        widgets = {
            'Name':        forms.TextInput(attrs={'class': 'form-control'}),
            'Description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'MacAddress':  forms.TextInput(attrs={'class': 'form-control'}),
            'Tank':        forms.Select(attrs={'class': 'form-control'}),
            'SensorType':  forms.Select(attrs={'class': 'form-control'}),
            'SamplingRate': forms.Select(attrs={'class': 'form-control'}),
            'MqttBroker':  forms.TextInput(attrs={'class': 'form-control'}),
            'MqttPort':    forms.NumberInput(attrs={'class': 'form-control'}),
            'Status':      forms.Select(attrs={'class': 'form-control'}),
            'Owner':       forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'Name':        'Nombre del dispositivo',
            'MacAddress':  'MAC Address',
            'Tank':        'Tanque asociado',
            'SensorType':  'Tipo de sensor',
            'SamplingRate': 'Intervalo de muestreo',
            'MqttBroker':  'Broker MQTT',
            'MqttPort':    'Puerto MQTT',
            'Status':      'Estado',
            'Owner':       'Responsable',
        }
