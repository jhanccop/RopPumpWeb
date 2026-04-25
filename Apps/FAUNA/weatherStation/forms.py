from django import forms
from django.utils import timezone

from .models import WeatherStation, WeatherReading


class WeatherStationForm(forms.ModelForm):
    class Meta:
        model = WeatherStation
        fields = (
            'Owner',
            'StationName',
            'Description',
            'Latitude',
            'Longitude',
            'Altitude',
            'MacAddress',
            'TimeSleep',
            'HasTempHumidity',
            'HasSolarRadiation',
            'HasPrecipitation',
            'HasWind',
            'Status',
        )
        widgets = {
            'StationName': forms.TextInput(attrs={
                'class': 'input-group-field form-control',
                'placeholder': '',
            }),
            'Description': forms.Textarea(attrs={
                'class': 'input-group-field form-control',
                'rows': 3,
                'placeholder': '',
            }),
            'Latitude': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': 'any',
                'placeholder': '',
            }),
            'Longitude': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': 'any',
                'placeholder': '',
            }),
            'Altitude': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': 'any',
                'placeholder': '',
            }),
            'HasTempHumidity': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'HasSolarRadiation': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'HasPrecipitation': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'HasWind': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'MacAddress': forms.TextInput(attrs={
                'class': 'input-group-field form-control',
                'placeholder': '',
            }),
            'TimeSleep': forms.Select(attrs={
                'class': 'input-group-field form-control',
            }),
            'Status': forms.Select(attrs={
                'class': 'input-group-field form-control',
                'placeholder': '',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(WeatherStationForm, self).__init__(*args, **kwargs)


class WeatherReadingForm(forms.ModelForm):
    class Meta:
        model = WeatherReading
        fields = (
            'Station',
            'DateCreate',
            'Temperature',
            'Humidity',
            'SolarRadiation',
            'Precipitation',
            'WindSpeed',
            'WindDirection',
        )
        widgets = {
            'Station': forms.Select(attrs={
                'class': 'input-group-field form-control',
            }),
            'DateCreate': forms.DateTimeInput(attrs={
                'class': 'input-group-field form-control',
                'type': 'datetime-local',
            }),
            'Temperature': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'placeholder': '°C',
            }),
            'Humidity': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'placeholder': '%',
            }),
            'SolarRadiation': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'placeholder': 'W/m²',
            }),
            'Precipitation': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'placeholder': 'mm',
            }),
            'WindSpeed': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'placeholder': 'm/s',
            }),
            'WindDirection': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.1',
                'placeholder': '0–360°',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(WeatherReadingForm, self).__init__(*args, **kwargs)
        self.fields['Station'].queryset = WeatherStation.objects.get_by_company(
            self.request.user.CompanyId.CompanyName
        )


class ReportFilterForm(forms.Form):
    station = forms.ModelChoiceField(
        queryset=WeatherStation.objects.none(),
        required=False,
        empty_label='All stations',
        widget=forms.Select(attrs={'class': 'input-group-field form-control'}),
    )
    date_from = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'input-group-field form-control',
            'type': 'date',
        }),
    )
    date_to = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'input-group-field form-control',
            'type': 'date',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ReportFilterForm, self).__init__(*args, **kwargs)
        self.fields['station'].queryset = WeatherStation.objects.get_by_company(
            self.request.user.CompanyId.CompanyName
        )

    def clean(self):
        cleaned = super().clean()
        d_from = cleaned.get('date_from')
        d_to = cleaned.get('date_to')
        if d_from and d_to and d_from > d_to:
            raise forms.ValidationError('Start date must be before end date.')
        return cleaned
