from django import forms
from Apps.wells.models import well
from Apps.field.models import Field
from Apps.batteries.models import Battery
from Apps.groups.models import Group

class CreateDataForm(forms.ModelForm):
    #import_file = forms.FileField(required=False)

    FieldName = forms.ModelChoiceField(
        queryset = Field.objects.filter(Company=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            }),
        required=True,
        to_field_name="FieldName",
        help_text="Field Name",
        initial=True
        )

    BatteryName = forms.ModelChoiceField(
        queryset = Battery.objects.filter(Company=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        required=True,
        to_field_name="BatteryName",
        help_text="Battery Name",
        initial=True
        )

    GroupName = forms.ModelChoiceField(
        queryset = Group.objects.filter(Company=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        required=True,
        to_field_name="GroupName",
        help_text="Group Name",
        initial=True
        )
    
    StrokeLength = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control me-2 text-end",
            "type": "number",
        }),
        required=True
    )

    PolishedRodDiameter = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number",
        }),
        required=True
    )

    TYPE_MOTOR_CHOICES = (
        ("Electric", "Electric"),
        ("Gas", "Gas"),
    )

    MotorType = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'type':"text",
            }),
        
        choices=TYPE_MOTOR_CHOICES,
        required=True
    )

    PumpIntake = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=True
    )

    PlungerDiameter = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=True
    )

    TrueVerticalDepth = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=True
    )

    TotalRodLength = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=True
    )

    TotalRodWeight = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control text-end",
            "type": "number"
        }),
        required=True
    )
    
    class Meta:
        model = well
        fields = (
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
                    "class":"choises",
                    "id":"PumpNameSelect",
                    "required": "true",
                }
            ),
            
        }

        
