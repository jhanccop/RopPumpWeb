from django import forms
from .models import ProductionFluid

class CreateDataForm(forms.ModelForm):
    #import_file = forms.FileField(required=False)
    DateCreate = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control datetimepicker text-center",
            "type": "text"
        }),
        required=True
    )
    
    OilProd = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "type": "number",
        }),
        required=False
    )

    WaterProd = forms.IntegerField(
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
            "UserAuthor",
            "OilProd",
            "WaterProd"
        )

        widgets = {
            'PumpName': forms.HiddenInput(
                attrs = {
                    "class":"multisteps-form__select form-control text-center",
                    "required":"true",
                    "type": "hidden",
                }
            ),

            'UserAuthor': forms.HiddenInput(
                attrs = {
                    "class":"multisteps-form__select form-control text-center",
                    "required":"true",
                    "type": "hidden",
                }
            )
        }

