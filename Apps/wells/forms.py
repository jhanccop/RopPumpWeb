from django import forms
from Apps.wells.models import well

class CreateDataForm(forms.ModelForm):
    #import_file = forms.FileField(required=False)

    PumpName = forms.ModelChoiceField(
        queryset = well.objects.filter(FieldName__Company=1), # put compnay id manually
        initial = None,
        required=True,
        to_field_name="PumpName"
        )
    
    StrokeLength = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number",
        }),
        required=True
    )

    PolishedRodDiameter = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number",
        }),
        required=True
    )

    PumpIntake = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number"
        }),
        required=True
    )

    PlungerDiameter = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number"
        }),
        required=True
    )

    TrueVerticalDepth = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number"
        }),
        required=True
    )

    TotalRodLength = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number"
        }),
        required=True
    )

    TotalRodWeight = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center",
            "type": "number"
        }),
        required=True
    )
    
    class Meta:
        model = well
        fields = (
            "PumpName",
            "FieldName",
            "BatteryName",
            "GroupName",
            "StrokeLength",
            "MotorType",
            "PolishedRodDiameter",
            "PumpIntake",
            "PlungerDiameter",
            "TrueVerticalDepth",
            "TotalRodLength",
            "TotalRodWeight"
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

        
