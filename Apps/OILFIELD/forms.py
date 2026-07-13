from django import forms

from .models import (
    AlertRule,
    Battery,
    Manifold,
    OperationalAlert,
    PumpingUnit,
    Tank,
    TankReading,
    Well,
    WellDailyProduction,
    WellEvent,
)

_FC = 'input-group-field form-control'


# ---------------------------------------------------------------------------
# BatteryForm
# ---------------------------------------------------------------------------

class BatteryForm(forms.ModelForm):
    class Meta:
        model = Battery
        fields = (
            'Owner',
            'Name',
            'Code',
            'Description',
            'Location',
            'Latitude',
            'Longitude',
            'Status',
        )
        widgets = {
            'Owner':       forms.Select(attrs={'class': _FC}),
            'Name':        forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Code':        forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Description': forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
            'Location':    forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Latitude':    forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Longitude':   forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Status':      forms.Select(attrs={'class': _FC}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


# ---------------------------------------------------------------------------
# ManifoldForm
# ---------------------------------------------------------------------------

class ManifoldForm(forms.ModelForm):
    class Meta:
        model = Manifold
        fields = (
            'Battery',
            'Name',
            'Code',
            'MaxPressure',
            'Status',
        )
        widgets = {
            'Battery':     forms.Select(attrs={'class': _FC}),
            'Name':        forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Code':        forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'MaxPressure': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Status':      forms.Select(attrs={'class': _FC}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Battery'].queryset = Battery.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# TankForm
# ---------------------------------------------------------------------------

class TankForm(forms.ModelForm):
    class Meta:
        model = Tank
        fields = (
            'Owner',
            'Battery',
            'Name',
            'Code',
            'Type',
            'NominalCapacity',
            'WorkingCapacity',
            'Material',
            'Diameter',
            'Height',
            'SensorType',
            'LowLevelAlert',
            'HighLevelAlert',
            'InstallationDate',
            'Status',
            'Latitude',
            'Longitude',
        )
        widgets = {
            'Owner':            forms.Select(attrs={'class': _FC}),
            'Battery':          forms.Select(attrs={'class': _FC}),
            'Name':             forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Code':             forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Type':             forms.Select(attrs={'class': _FC}),
            'NominalCapacity':  forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'WorkingCapacity':  forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Material':         forms.Select(attrs={'class': _FC}),
            'Diameter':         forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Height':           forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'SensorType':       forms.Select(attrs={'class': _FC}),
            'LowLevelAlert':    forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'HighLevelAlert':   forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'InstallationDate': forms.DateInput(
                attrs={'class': _FC, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'Status':    forms.Select(attrs={'class': _FC}),
            'Latitude':  forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Longitude': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Battery'].queryset = Battery.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# PumpingUnitForm
# ---------------------------------------------------------------------------

class PumpingUnitForm(forms.ModelForm):
    class Meta:
        model = PumpingUnit
        fields = (
            'Name',
            'Code',
            'Type',
            'Manufacturer',
            'Model',
            'StrokeLength',
            'MaxSPM',
            'MaxLoad',
            'MotorPower',
            'GearboxRating',
            'InstallationDate',
            'Status',
        )
        widgets = {
            'Name':             forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Code':             forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Type':             forms.Select(attrs={'class': _FC}),
            'Manufacturer':     forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Model':            forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'StrokeLength':     forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'MaxSPM':           forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'MaxLoad':          forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'MotorPower':       forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'GearboxRating':    forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'InstallationDate': forms.DateInput(
                attrs={'class': _FC, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'Status': forms.Select(attrs={'class': _FC}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


# ---------------------------------------------------------------------------
# WellForm
# ---------------------------------------------------------------------------

class WellForm(forms.ModelForm):
    class Meta:
        model = Well
        fields = (
            'Owner',
            'Manifold',
            'Tank',
            'PumpingUnit',
            'Code',
            'Name',
            'FieldName',
            'Description',
            'TotalDepth',
            'PumpDepth',
            'PumpDiameter',
            'LiftType',
            'InstallationDate',
            'ProductionTarget',
            'Status',
            'Latitude',
            'Longitude',
            'Notes',
        )
        widgets = {
            'Owner':            forms.Select(attrs={'class': _FC}),
            'Manifold':         forms.Select(attrs={'class': _FC}),
            'Tank':             forms.Select(attrs={'class': _FC}),
            'PumpingUnit':      forms.Select(attrs={'class': _FC}),
            'Code':             forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Name':             forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'FieldName':        forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
            'Description':      forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
            'TotalDepth':       forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'PumpDepth':        forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'PumpDiameter':     forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'LiftType':         forms.Select(attrs={'class': _FC}),
            'InstallationDate': forms.DateInput(
                attrs={'class': _FC, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'ProductionTarget': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Status':           forms.Select(attrs={'class': _FC}),
            'Latitude':         forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Longitude':        forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Notes':            forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Manifold'].queryset   = Manifold.objects.filter(
                Battery__Owner__CompanyId__CompanyName=company
            )
            self.fields['Tank'].queryset       = Tank.objects.get_by_company(company)
            self.fields['PumpingUnit'].queryset = PumpingUnit.objects.all()


# ---------------------------------------------------------------------------
# WellDailyProductionForm
# ---------------------------------------------------------------------------

class WellDailyProductionForm(forms.ModelForm):
    class Meta:
        model = WellDailyProduction
        fields = (
            'Tank',
            'OperativeDate',
            'TankLevelStart',
            'TankLevelEnd',
            'TankProduction',
            'OilProduction',
            'WaterProduction',
            'GasProduction',
            'RunTime',
            'SPM',
            'Fillage',
            'OperationalCondition',
            'DeferredProduction',
            'Observations',
        )
        widgets = {
            'Tank':                 forms.Select(attrs={'class': _FC}),
            'OperativeDate':        forms.DateInput(
                attrs={'class': _FC, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'OilProduction':        forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'WaterProduction':      forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'GasProduction':        forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'RunTime':              forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'SPM':                  forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Fillage':              forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'OperationalCondition': forms.Select(attrs={'class': _FC}),
            'DeferredProduction':   forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Tank':                 forms.Select(attrs={'class': _FC}),
            'TankLevelStart':       forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'TankLevelEnd':         forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'TankProduction':       forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Observations':         forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Tank'].queryset = Tank.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# TankReadingForm
# ---------------------------------------------------------------------------

class TankReadingForm(forms.ModelForm):
    class Meta:
        model = TankReading
        fields = (
            'Tank',
            'ReadingDate',
            'Level',
            'Temperature',
            'WaterLevel',
            'Volume',
            'Source',
            'Notes',
        )
        widgets = {
            'Tank':        forms.Select(attrs={'class': _FC}),
            'ReadingDate': forms.DateTimeInput(
                attrs={'class': _FC, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'Level':       forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Temperature': forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'WaterLevel':  forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Volume':      forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'Source':      forms.Select(attrs={'class': _FC}),
            'Notes':       forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Tank'].queryset = Tank.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# WellEventForm
# ---------------------------------------------------------------------------

class WellEventForm(forms.ModelForm):
    class Meta:
        model = WellEvent
        fields = (
            'Well',
            'EventType',
            'EventDate',
            'Description',
        )
        widgets = {
            'Well':        forms.Select(attrs={'class': _FC}),
            'EventType':   forms.Select(attrs={'class': _FC}),
            'EventDate':   forms.DateTimeInput(
                attrs={'class': _FC, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'Description': forms.Textarea(attrs={'class': _FC, 'rows': 3, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Well'].queryset = Well.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# AlertRuleForm
# ---------------------------------------------------------------------------

class AlertRuleForm(forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = (
            'AssetType',
            'Well',
            'Tank',
            'Variable',
            'Condition',
            'Threshold',
            'AlertType',
            'Severity',
            'IsActive',
            'Description',
        )
        widgets = {
            'AssetType':   forms.Select(attrs={'class': _FC}),
            'Well':        forms.Select(attrs={'class': _FC}),
            'Tank':        forms.Select(attrs={'class': _FC}),
            'Variable':    forms.Select(attrs={'class': _FC}),
            'Condition':   forms.Select(attrs={'class': _FC}),
            'Threshold':   forms.NumberInput(attrs={'class': _FC, 'step': 'any', 'placeholder': ''}),
            'AlertType':   forms.Select(attrs={'class': _FC}),
            'Severity':    forms.Select(attrs={'class': _FC}),
            'IsActive':    forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Description': forms.TextInput(attrs={'class': _FC, 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request is not None:
            company = self.request.user.CompanyId.CompanyName
            self.fields['Well'].queryset = Well.objects.get_by_company(company)
            self.fields['Tank'].queryset = Tank.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# AlertFilterForm
# ---------------------------------------------------------------------------

class AlertFilterForm(forms.Form):
    well = forms.ModelChoiceField(
        queryset=Well.objects.none(),
        required=False,
        empty_label='Todos los pozos',
        widget=forms.Select(attrs={'class': _FC}),
    )
    battery = forms.ModelChoiceField(
        queryset=Battery.objects.none(),
        required=False,
        empty_label='Todas las baterías',
        widget=forms.Select(attrs={'class': _FC}),
    )
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las severidades')] + list(OperationalAlert.SEVERITY_CHOICES),
        widget=forms.Select(attrs={'class': _FC}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + list(OperationalAlert.STATUS_CHOICES),
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
            self.fields['well'].queryset    = Well.objects.get_by_company(company)
            self.fields['battery'].queryset = Battery.objects.get_by_company(company)


# ---------------------------------------------------------------------------
# ProductionFilterForm
# ---------------------------------------------------------------------------

class ProductionFilterForm(forms.Form):
    well = forms.ModelChoiceField(
        queryset=Well.objects.none(),
        required=False,
        empty_label='Todos los pozos',
        widget=forms.Select(attrs={'class': _FC}),
    )
    battery = forms.ModelChoiceField(
        queryset=Battery.objects.none(),
        required=False,
        empty_label='Todas las baterías',
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
            self.fields['well'].queryset    = Well.objects.get_by_company(company)
            self.fields['battery'].queryset = Battery.objects.get_by_company(company)
