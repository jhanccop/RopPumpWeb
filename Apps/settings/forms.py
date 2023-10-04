from django import forms
from .models import setting
from Apps.wells.models import well

class UpdateDataForm(forms.ModelForm):
    #import_file = forms.FileField(required=False)

    PumpName = forms.ModelChoiceField(
        queryset = well.objects.filter(FieldName__Company=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            }),
        required=True,
        to_field_name="PumpName",
        help_text="Pump Name",
        initial=True

        )
    
    Types_CHOICES = (
        ("Rod Pump Analyzer","Rod Pump Analyzer"),
        ("Tank Level Meter","Tank Level Meter")
    )
    DeviceType = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        choices=Types_CHOICES,
        required=True
    )

    AVAILABLE_CHOICES = (
        (True, "Available"),
        (False, "No available"),
    )
    Available = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        choices=AVAILABLE_CHOICES,
        required=True
    )

    MacAddress = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control text-end",
            "type": "text"
        }),
        required=True
    )

    IpAddress = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control text-end",
            "type": "text"
        }),
        required=False
    )
    
    TimeOn = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=False
    )

    TimeOff = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=False
    )

    ThresholdAlert1 = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=False
    )

    ThresholdAlert2 = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )

    ThresholdStop = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )

    REFRESH_CHOICES = (
        (30,"30s"),
        (60,"1m"),
        (120,"2m"),
        (300,"5m"),
        (600,"10m"),
        (900,"15m"),
        (1800,"30m"),
    )

    Refresh = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        choices=REFRESH_CHOICES,
        required=True
    )

    TankHeight = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )

    TankFactor = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )
    
    class Meta:
        model = setting
        fields = (
            "PumpName",
            "DeviceType",
            "Available",
            "MacAddress",
            "IpAddress",
            "TimeOn",
            "TimeOff",
            "ThresholdAlert1",
            "ThresholdAlert2",
            "ThresholdStop",
            "Refresh",
            "TankFactor",
            "TankHeight"
        )
        widgets = {

            'PumpName': forms.HiddenInput(
                attrs={
                    "class":"form-control",
                    "id":"PumpNameSelect",
                    "required": "true",
                }
            ),
            'DateTest' : forms.DateInput(
                attrs={
                    "class": "form-control datetimepicker text-center",
                    "type": "date",
                    "required":True
                }
            ),
        }

class CreateDataForm(forms.ModelForm):
    #import_file = forms.FileField(required=False)

    DeviceName = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control text-end",
            "type": "text"
        }),
        required=True
    )

    PumpName = forms.ModelChoiceField(
        queryset = well.objects.filter(FieldName__Company=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            }),
        required=True,
        to_field_name="PumpName",
        help_text="Pump Name",
        initial=True

        )
    
    Types_CHOICES = (
        ("Rod Pump Analyzer","Rod Pump Analyzer"),
        ("Tank Level Meter","Tank Level Meter")
    )
    DeviceType = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        choices=Types_CHOICES,
        required=True
    )

    AVAILABLE_CHOICES = (
        (True, "Available"),
        (False, "No available"),
    )

    Available = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        choices=AVAILABLE_CHOICES,
        required=True
    )

    MacAddress = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control text-end",
            "type": "text"
        }),
        required=True
    )

    IpAddress = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control text-end",
            "type": "text"
        }),
        required=False
    )
    
    TimeOn = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=False
    )

    TimeOff = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=False
    )

    ThresholdAlert1 = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=False
    )

    ThresholdAlert2 = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )

    ThresholdStop = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )

    REFRESH_CHOICES = (
        (30,"30s"),
        (60,"1m"),
        (120,"2m"),
        (300,"5m"),
        (600,"10m"),
        (900,"15m"),
        (1800,"30m"),
    )

    Refresh = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        choices=REFRESH_CHOICES,
        required=True
    )

    TankHeight = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )

    TankFactor = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=False
    )
    
    class Meta:
        model = setting
        fields = (
            "DeviceName",
            "PumpName",
            "DeviceType",
            "Available",
            "MacAddress",
            "IpAddress",
            "TimeOn",
            "TimeOff",
            "ThresholdAlert1",
            "ThresholdAlert2",
            "ThresholdStop",
            "Refresh",
            "TankFactor",
            "TankHeight"
        )
        


