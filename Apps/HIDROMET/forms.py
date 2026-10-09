from django import forms

from .models import HydroStation, HydroReading


_INPUT = 'input-group-field form-control'


def _num(step='any', placeholder=''):
    return forms.NumberInput(attrs={'class': _INPUT, 'step': step, 'placeholder': placeholder})


def _check():
    return forms.CheckboxInput(attrs={'class': 'form-check-input'})


class HydroStationForm(forms.ModelForm):
    class Meta:
        model = HydroStation
        fields = (
            'Owner',
            'StationName',
            'Description',
            'Latitude',
            'Longitude',
            'Altitude',
            'WaterBodyType',
            'WaterBodyName',
            'LevelTare',
            'LevelWarning',
            'LevelCritical',
            'MacAddress',
            'TimeSleep',
            'HasTempHumidity',
            'HasSolarRadiation',
            'HasPrecipitation',
            'HasWind',
            'HasWaterLevel',
            'HasWaterPH',
            'HasWaterTemp',
            'Status',
        )
        widgets = {
            'StationName': forms.TextInput(attrs={'class': _INPUT}),
            'Description': forms.Textarea(attrs={'class': _INPUT, 'rows': 3}),
            'Latitude': _num(),
            'Longitude': _num(),
            'Altitude': _num(),
            'WaterBodyType': forms.Select(attrs={'class': _INPUT}),
            'WaterBodyName': forms.TextInput(attrs={'class': _INPUT}),
            'LevelTare': _num('0.001'),
            'LevelWarning': _num('0.01'),
            'LevelCritical': _num('0.01'),
            'MacAddress': forms.TextInput(attrs={'class': _INPUT}),
            'TimeSleep': forms.Select(attrs={'class': _INPUT}),
            'HasTempHumidity': _check(),
            'HasSolarRadiation': _check(),
            'HasPrecipitation': _check(),
            'HasWind': _check(),
            'HasWaterLevel': _check(),
            'HasWaterPH': _check(),
            'HasWaterTemp': _check(),
            'Status': forms.Select(attrs={'class': _INPUT}),
        }

    recalc_history = forms.BooleanField(
        required=False,
        label='Recalcular el histórico con esta tara',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(HydroStationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        warning = cleaned.get('LevelWarning')
        critical = cleaned.get('LevelCritical')
        if warning is not None and critical is not None and warning >= critical:
            raise forms.ValidationError('El nivel de alerta debe ser menor que el nivel crítico.')
        tare = cleaned.get('LevelTare')
        if tare is not None and tare <= 0:
            self.add_error('LevelTare', 'La tara debe ser mayor que 0.')
        if cleaned.get('recalc_history') and tare is None:
            self.add_error('recalc_history', 'Configura la tara para recalcular el histórico.')
        return cleaned


class HydroReadingForm(forms.ModelForm):
    class Meta:
        model = HydroReading
        fields = (
            'Station',
            'DateCreate',
            'Temperature',
            'Humidity',
            'WindDirection',
            'WindSpeed',
            'Precipitation',
            'SolarRadiation',
            'RawDistance',
            'WaterPH',
            'WaterTemperature',
        )
        widgets = {
            'Station': forms.Select(attrs={'class': _INPUT}),
            'DateCreate': forms.DateTimeInput(attrs={'class': _INPUT, 'type': 'datetime-local'}),
            'Temperature': _num('0.01', '°C'),
            'Humidity': _num('0.01', '%'),
            'WindDirection': _num('0.1', '0–360°'),
            'WindSpeed': _num('0.01', 'm/s'),
            'Precipitation': _num('0.01', 'mm'),
            'SolarRadiation': _num('0.01', 'W/m²'),
            'RawDistance': _num('0.001', 'm desde el sensor'),
            'WaterPH': _num('0.01', '0–14'),
            'WaterTemperature': _num('0.01', '°C'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(HydroReadingForm, self).__init__(*args, **kwargs)
        self.fields['Station'].queryset = HydroStation.objects.get_by_company(
            self.request.user.CompanyId.CompanyName
        )

    def clean_WaterPH(self):
        ph = self.cleaned_data.get('WaterPH')
        if ph is not None and not 0 <= ph <= 14:
            raise forms.ValidationError('El pH debe estar entre 0 y 14.')
        return ph

    def clean_WindDirection(self):
        wd = self.cleaned_data.get('WindDirection')
        if wd is not None and not 0 <= wd <= 360:
            raise forms.ValidationError('La dirección debe estar entre 0 y 360°.')
        return wd


class ReportFilterForm(forms.Form):
    station = forms.ModelChoiceField(
        queryset=HydroStation.objects.none(),
        required=False,
        empty_label='Todas las estaciones',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    date_from = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ReportFilterForm, self).__init__(*args, **kwargs)
        self.fields['station'].queryset = HydroStation.objects.get_by_company(
            self.request.user.CompanyId.CompanyName
        )

    def clean(self):
        cleaned = super().clean()
        d_from = cleaned.get('date_from')
        d_to = cleaned.get('date_to')
        if d_from and d_to and d_from > d_to:
            raise forms.ValidationError('La fecha inicial debe ser anterior a la final.')
        return cleaned
