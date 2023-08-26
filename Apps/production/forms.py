from django import forms
from .models import ProductionFluid
from Apps.wells.models import well

class CreateDataForm(forms.ModelForm):
    #import_file = forms.FileField(required=False)

    PumpName = forms.ModelChoiceField(
        queryset = well.objects.filter(FieldName__Company=1), # put compnay id manually
        initial = None,
        required=True,
        to_field_name="PumpName"
        )
    
    OilProd = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "type": "number",
        }),
        required=True
    )

    WaterProd = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "type": "number"
        }),
        required=True
    )
    
    class Meta:
        model = ProductionFluid
        fields = (
            "PumpName",
            "DateTest",
            "OilProd",
            "WaterProd"
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

        
