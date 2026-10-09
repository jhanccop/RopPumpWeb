from django import forms
from .models import (
    SecurityDevice, Sensor, SENSOR_KEYS, CATEGORY_CHOICES,
    TelegramConfig, TelegramRecipient,
)


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


class TelegramConfigForm(forms.ModelForm):
    class Meta:
        model  = TelegramConfig
        fields = ['Enabled', 'BotToken', 'OnlyActiveState',
                  'NotifyDeviceOffline', 'OfflineThresholdMinutes',
                  'NotifyDeviceReconnect', 'CooldownSeconds']
        widgets = {
            'Enabled':                 forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'BotToken':                forms.TextInput(attrs={'class': 'form-control',
                                                               'autocomplete': 'off',
                                                               'placeholder': '123456789:AA...'}),
            'OnlyActiveState':         forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'NotifyDeviceOffline':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'OfflineThresholdMinutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'NotifyDeviceReconnect':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'CooldownSeconds':         forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'Enabled':                 'Notificaciones activas',
            'BotToken':                'Token del Bot',
            'OnlyActiveState':         'Solo notificar estado "activo"',
            'NotifyDeviceOffline':     'Notificar dispositivo desconectado',
            'OfflineThresholdMinutes': 'Umbral de desconexión (minutos)',
            'NotifyDeviceReconnect':   'Notificar reconexión',
            'CooldownSeconds':         'Anti-spam entre alertas repetidas (segundos)',
        }


class TelegramRecipientForm(forms.ModelForm):
    class Meta:
        model  = TelegramRecipient
        fields = ['ChatID', 'Label', 'Enabled',
                  'NotifyCritico', 'NotifyAlto', 'NotifyInformativo',
                  'NotifyDeviceOffline', 'NotifyDeviceReconnect']
        widgets = {
            'ChatID':                forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                             'placeholder': 'ej. 123456789'}),
            'Label':                 forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                             'placeholder': 'ej. Jefe de seguridad'}),
            'Enabled':               forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'NotifyCritico':         forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'NotifyAlto':            forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'NotifyInformativo':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'NotifyDeviceOffline':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'NotifyDeviceReconnect': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
