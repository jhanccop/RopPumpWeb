from django import forms
from Apps.equipment.models import Tank, RodPumpWell,Environmental
from Apps.batteries.models import Battery
from Apps.field.models import Field
from Apps.groups.models import Group
from Apps.users.models import User

class TankForm(forms.ModelForm):
    class Meta:
        model = Tank
        fields = (
            'Owner',
            'TankName',
            'FieldName',
            'BatteryName',
            'GroupName',
            'LatLocation',
            'LonLocation',
            'SupervisorUser',
            'TankHeight',
            'TankFactor',
            'WellsAssigned',
            'Status'
        )
        
        widgets = {
            'TankName': forms.TextInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'FieldName': forms.Select(
                attrs = {
                    'placeholder': 'Cliente',
                    'class': 'input-group-field form-control',
                }
            ),
            'BatteryName': forms.Select(
                attrs = {
                    'placeholder': 'Transformador',
                    'class': 'input-group-field form-control',
                }
            ),
            'GroupName': forms.Select(
                attrs = {
                    'placeholder': 'Transformador',
                    'class': 'input-group-field form-control',
                }
            ),
            'LatLocation': forms.NumberInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'LonLocation': forms.NumberInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'SupervisorUser': forms.Select(
                attrs = {
                    'placeholder': 'Transformador',
                    'class': 'input-group-field form-control',
                }
            ),
            'TankHeight': forms.NumberInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'TankFactor': forms.NumberInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'WellsAssigned': forms.SelectMultiple(
                attrs = {
                    'class': 'input-group-field form-control',
                }
            ),
            'Status': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
        }

    def clean_TankHeight(self):
        TankHeight = self.cleaned_data['TankHeight']
        if not TankHeight > 0:
            raise forms.ValidationError('Enter a valid value')

        return TankHeight

    def clean_TankFactor(self):
        TankFactor = self.cleaned_data['TankFactor']
        if not TankFactor > 0:
            raise forms.ValidationError('Enter a valid value')

        return TankFactor
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TankForm, self).__init__(*args, **kwargs)
        self.fields['FieldName'].queryset = Field.objects.filter(Company__id = self.request.user.CompanyId.id)
        self.fields['BatteryName'].queryset = Battery.objects.filter(Company__id = self.request.user.CompanyId.id)
        self.fields['GroupName'].queryset = Group.objects.filter(Company__id = self.request.user.CompanyId.id)
        self.fields['SupervisorUser'].queryset = User.objects.filter(CompanyId__id = self.request.user.CompanyId.id)
        self.fields['WellsAssigned'].queryset = RodPumpWell.objects.filter(FieldName__Company__id = self.request.user.CompanyId.id)
    
class EnvironmentalForm(forms.ModelForm):
    class Meta:
        model = Environmental
        fields = (
            'Owner',
            'EnvironmentalName',
            'GroupName',
            'LatLocation',
            'LonLocation',
            'SupervisorUser',
            'Status'
        )
        
        widgets = {
            'EnvironmentalName': forms.TextInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'GroupName': forms.Select(
                attrs = {
                    'placeholder': 'Transformador',
                    'class': 'input-group-field form-control',
                }
            ),
            'LatLocation': forms.NumberInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'LonLocation': forms.NumberInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'SupervisorUser': forms.Select(
                attrs = {
                    'placeholder': 'Transformador',
                    'class': 'input-group-field form-control',
                }
            ),
            'Status': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(EnvironmentalForm, self).__init__(*args, **kwargs)
        self.fields['GroupName'].queryset = Group.objects.filter(Company__id = self.request.user.CompanyId.id)
        self.fields['SupervisorUser'].queryset = User.objects.filter(CompanyId__id = self.request.user.CompanyId.id)

class RodPumpWellForm(forms.ModelForm):
    FieldName = forms.ModelChoiceField(
        queryset = RodPumpWell.objects.filter(WellName=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            }),
        required=True,
        to_field_name="FieldName",
        help_text="Field Name",
        initial=True
        )