from django import forms

from .models import Alert, AlertRule, ElectricalReading, Substation, Transformer

_FC = 'input-group-field form-control'


# ---------------------------------------------------------------------------
# TransformerForm
# ---------------------------------------------------------------------------

class TransformerForm(forms.ModelForm):
    class Meta:
        model = Transformer
        fields = (
            'Owner',
            'Code',
            'Series',
            'StationName',
            'Description',
            'NominalPower',
            'PrimaryVoltage',
            'SecondaryVoltage',
            'Type',
            'CoolingType',
            'Manufacturer',
            'Model',
            'YearManufacture',
            'InstallationDate',
            'EstimatedLifespan',
            'Status',
            'Latitude',
            'Longitude',
            'Address',
            'Substation',
        )
        widgets = {
            'Owner': forms.Select(attrs={'class': _FC}),
            'Code': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Series': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'StationName': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Description': forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
            'NominalPower': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'PrimaryVoltage': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'SecondaryVoltage': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Type': forms.Select(attrs={'class': _FC}),
            'CoolingType': forms.Select(attrs={'class': _FC}),
            'Manufacturer': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Model': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'YearManufacture': forms.NumberInput(attrs={'class': _FC, 'placeholder': ''}),
            'InstallationDate': forms.DateInput(
                attrs={'class': _FC, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'EstimatedLifespan': forms.NumberInput(attrs={'class': _FC, 'placeholder': '25'}),
            'Status': forms.Select(attrs={'class': _FC}),
            'Latitude': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Longitude': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Address': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Substation': forms.Select(attrs={'class': _FC}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


# ---------------------------------------------------------------------------
# SubstationForm
# ---------------------------------------------------------------------------

class SubstationForm(forms.ModelForm):
    class Meta:
        model = Substation
        fields = (
            'Owner',
            'Name',
            'Description',
            'Type',
            'Status',
            'NominalVoltage',
            'InstalledCapacity',
            'Latitude',
            'Longitude',
            'Address',
        )
        widgets = {
            'Owner': forms.Select(attrs={'class': _FC}),
            'Name': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Description': forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
            'Type': forms.Select(attrs={'class': _FC}),
            'Status': forms.Select(attrs={'class': _FC}),
            'NominalVoltage': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'InstalledCapacity': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Latitude': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Longitude': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Address': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


# ---------------------------------------------------------------------------
# AlertRuleForm
# ---------------------------------------------------------------------------

class AlertRuleForm(forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = (
            'Transformer',
            'Variable',
            'Condition',
            'Threshold',
            'Severity',
            'IsActive',
            'Description',
        )
        widgets = {
            'Transformer': forms.Select(attrs={'class': _FC}),
            'Variable': forms.Select(attrs={'class': _FC}),
            'Condition': forms.Select(attrs={'class': _FC}),
            'Threshold': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Severity': forms.Select(attrs={'class': _FC}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Description': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Transformer'].queryset = Transformer.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# AlertFilterForm
# ---------------------------------------------------------------------------

class AlertFilterForm(forms.Form):
    transformer = forms.ModelChoiceField(
        queryset=Transformer.objects.none(),
        required=False,
        empty_label='Todos los transformadores',
        widget=forms.Select(attrs={'class': _FC}),
    )
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las severidades')] + list(Alert.SEVERITY_CHOICES),
        widget=forms.Select(attrs={'class': _FC}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + list(Alert.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': _FC}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': _FC, 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': _FC, 'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['transformer'].queryset = Transformer.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# ElectricalReadingForm
# ---------------------------------------------------------------------------

class ElectricalReadingForm(forms.ModelForm):
    class Meta:
        model = ElectricalReading
        fields = (
            'Transformer',
            'HotSpotTemperature',
            'OilTemperature',
            'AmbientTemperature',
            'InternalPressure',
            'OilLevel',
            'Vibration',
            'OilHumidity',
        )
        widgets = {
            'Transformer': forms.Select(attrs={'class': _FC}),
            'HotSpotTemperature': forms.NumberInput(attrs={'class': _FC, 'step': '0.1', 'placeholder': ''}),
            'OilTemperature': forms.NumberInput(attrs={'class': _FC, 'step': '0.1', 'placeholder': ''}),
            'AmbientTemperature': forms.NumberInput(attrs={'class': _FC, 'step': '0.1', 'placeholder': ''}),
            'InternalPressure': forms.NumberInput(attrs={'class': _FC, 'step': '0.1', 'placeholder': ''}),
            'OilLevel': forms.NumberInput(attrs={'class': _FC, 'step': '0.1', 'placeholder': ''}),
            'Vibration': forms.NumberInput(attrs={'class': _FC, 'step': '0.01', 'placeholder': ''}),
            'OilHumidity': forms.NumberInput(attrs={'class': _FC, 'step': '0.1', 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
