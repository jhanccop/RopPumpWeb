from django import forms
from django.forms import inlineformset_factory
from datetime import date, timedelta

from .models import CameraStation, CameraCapture, CaptureDetection, SpeciesLabel


class CameraStationForm(forms.ModelForm):
    class Meta:
        model = CameraStation
        fields = (
            'Owner',
            'StationName',
            'Description',
            'Latitude',
            'Longitude',
            'Altitude',
            'MacAddress',
            'TurnOnTime',
            'TurnOffTime',
            'TimeSleep',
            'TimeSleepC',
            'Sensitivity',
            'HasTempHumidity',
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
            'MacAddress': forms.TextInput(attrs={
                'class': 'input-group-field form-control',
                'placeholder': '',
            }),
            'TurnOnTime': forms.TimeInput(attrs={
                'class': 'input-group-field form-control',
                'type': 'time',
            }),
            'TurnOffTime': forms.TimeInput(attrs={
                'class': 'input-group-field form-control',
                'type': 'time',
            }),
            'TimeSleep': forms.Select(attrs={
                'class': 'input-group-field form-control',
            }),
            'TimeSleepC': forms.Select(attrs={
                'class': 'input-group-field form-control',
            }),
            'Sensitivity': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'min': '0',
                'max': '1',
                'placeholder': '0.6',
            }),
            'HasTempHumidity': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'Status': forms.Select(attrs={
                'class': 'input-group-field form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)


class CameraCaptureForm(forms.ModelForm):
    class Meta:
        model = CameraCapture
        fields = (
            'Station',
            'DateCapture',
            'Image',
            'Temperature',
            'Humidity',
            'VoltageBattery',
            'Notes',
        )
        widgets = {
            'Station': forms.Select(attrs={
                'class': 'input-group-field form-control',
            }),
            'DateCapture': forms.DateTimeInput(attrs={
                'class': 'input-group-field form-control',
                'type': 'datetime-local',
            }),
            'Image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'Temperature': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.1',
                'placeholder': '',
            }),
            'Humidity': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.1',
                'placeholder': '',
            }),
            'VoltageBattery': forms.NumberInput(attrs={
                'class': 'input-group-field form-control',
                'step': '0.01',
                'placeholder': '',
            }),
            'Notes': forms.Textarea(attrs={
                'class': 'input-group-field form-control',
                'rows': 2,
                'placeholder': '',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['Station'].queryset = CameraStation.objects.get_by_company(
            self.request.user.CompanyId.CompanyName
        )


class CaptureDetectionForm(forms.ModelForm):
    class Meta:
        model = CaptureDetection
        fields = ('Species', 'Count')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', '— select —')] + [
            (sl.Name, f'{sl.ClassId} — {sl.Name}')
            for sl in SpeciesLabel.objects.order_by('ClassId')
        ]
        self.fields['Species'].widget = forms.Select(
            choices=choices,
            attrs={'class': 'form-control form-control-sm'},
        )
        self.fields['Count'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'min': '0',
        })


DetectionFormSet = inlineformset_factory(
    CameraCapture,
    CaptureDetection,
    form=CaptureDetectionForm,
    extra=1,
    can_delete=True,
)


class CaptureReportFilterForm(forms.Form):
    station = forms.ModelChoiceField(
        queryset=CameraStation.objects.none(),
        required=False,
        empty_label='All stations',
        widget=forms.Select(attrs={'class': 'input-group-field form-control'}),
    )
    species = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-group-field form-control',
            'placeholder': '',
            'list': 'species-list',
        }),
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
        super().__init__(*args, **kwargs)
        self.fields['station'].queryset = CameraStation.objects.get_by_company(
            self.request.user.CompanyId.CompanyName
        )

    def clean(self):
        cleaned = super().clean()
        d_from = cleaned.get('date_from')
        d_to = cleaned.get('date_to')
        if d_from and d_to and d_from > d_to:
            raise forms.ValidationError('Start date must be before end date.')
        return cleaned
