from django import forms
from .models import WellAnalyzerStation


class WellAnalyzerStationForm(forms.ModelForm):
    class Meta:
        model  = WellAnalyzerStation
        fields = [
            'Name', 'Description', 'MacAddress', 'Well',
            'SamplingRate', 'MqttBroker', 'MqttPort',
            'Status', 'Owner',
        ]
        widgets = {
            'Name':        forms.TextInput(attrs={'class': 'form-control'}),
            'Description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'MacAddress':  forms.TextInput(attrs={'class': 'form-control'}),
            'Well':        forms.Select(attrs={'class': 'form-control'}),
            'SamplingRate': forms.Select(attrs={'class': 'form-control'}),
            'MqttBroker':  forms.TextInput(attrs={'class': 'form-control'}),
            'MqttPort':    forms.NumberInput(attrs={'class': 'form-control'}),
            'Status':      forms.Select(attrs={'class': 'form-control'}),
            'Owner':       forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'Name':        'Nombre del dispositivo',
            'MacAddress':  'MAC Address',
            'Well':        'Pozo asociado',
            'SamplingRate': 'Intervalo de muestreo',
            'MqttBroker':  'Broker MQTT',
            'MqttPort':    'Puerto MQTT',
            'Status':      'Estado',
            'Owner':       'Responsable',
        }
