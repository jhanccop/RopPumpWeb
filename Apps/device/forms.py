from django import forms
from Apps.device.models import TankDevice, WellAnalyzerDevice, EnvironmentalDevice
from Apps.equipment.models import Tank, Environmental

class TankForm(forms.ModelForm):
    class Meta:
        model = TankDevice
        fields = (
            'Owner',
            'DeviceName',
            'DeviceMacAddress',
            'DeviceStatus',
            'SamplingRate',
            'IdTank',
        )
        
        widgets = {
            'DeviceName': forms.TextInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'DeviceMacAddress': forms.TextInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'DeviceStatus': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'SamplingRate': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'IdTank': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
        }

    def clean_SamplingRate(self):
        SamplingRate = self.cleaned_data['SamplingRate']
        if not SamplingRate > 0:
            raise forms.ValidationError('Enter a valid value')

        return SamplingRate
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TankForm, self).__init__(*args, **kwargs)
        self.fields['IdTank'].queryset = Tank.objects.filter(SupervisorUser__CompanyId__id = self.request.user.CompanyId.id)
    
class EnvironmentalForm(forms.ModelForm):
    class Meta:
        model = EnvironmentalDevice
        fields = (
            'Owner',
            'DeviceName',
            'DeviceMacAddress',
            'DeviceStatus',
            'SamplingRate',
            'IdEnvironmental',
        )
        
        widgets = {
            'DeviceName': forms.TextInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'DeviceMacAddress': forms.TextInput(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'DeviceStatus': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'SamplingRate': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
            'IdEnvironmental': forms.Select(
                attrs = {
                    'placeholder': '',
                    'class': 'input-group-field form-control',
                }
            ),
        }

    def clean_SamplingRate(self):
        SamplingRate = self.cleaned_data['SamplingRate']
        if not SamplingRate > 0:
            raise forms.ValidationError('Enter a valid value')

        return SamplingRate
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(EnvironmentalForm, self).__init__(*args, **kwargs)
        self.fields['IdEnvironmental'].queryset = Environmental.objects.filter(Owner__CompanyId__id = self.request.user.CompanyId.id)

class TankDataForm(forms.ModelForm):
    FieldName = forms.ModelChoiceField(
        queryset = TankDevice.objects.filter(IdTank=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            }),
        required=True,
        to_field_name="FieldName",
        help_text="Field Name",
        initial=True
        )

class AnalyzerDataForm(forms.ModelForm):
    FieldName = forms.ModelChoiceField(
        queryset = WellAnalyzerDevice.objects.filter(IdRodPumpWell=1), # put compnay id manually
        widget=forms.Select(attrs={
            'class': 'form-control',
            }),
        required=True,
        to_field_name="FieldName",
        help_text="Field Name",
        initial=True
        )