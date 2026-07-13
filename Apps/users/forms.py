from dataclasses import field
from django import forms
from django.contrib.auth import authenticate

from .models import User, Application
from Apps.company.models import Company


class UserRegisterForm(forms.ModelForm):

    UserName = forms.CharField(
        label="UserName",
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'UserName',
                'class': 'form-control form-control-lg',
            }
        )
    )

    Email = forms.CharField(
        label="Email",
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Email',
                'class': 'form-control form-control-lg',
            }
        )
    )

    Name = forms.CharField(
        label="Name",
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Name',
                'class': 'form-control form-control-lg',
            }
        )
    )

    LastName = forms.CharField(
        label="LastName",
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'LastName',
                'class': 'form-control form-control-lg',
            }
        )
    )

    password1 = forms.CharField(
        label="password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'password',
                'class': 'form-control form-control-lg',
            }
        )
    )

    password2 = forms.CharField(
        label="re-password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'repeat password',
                'class': 'form-control form-control-lg',
            }
        )
    )

    class Meta:
        model = User
        fields = (
            'UserName',
            'Email',
            'Name',
            'LastName',
            'CompanyId',
        )

    def clean_password2(self):
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            self.add_error("password2", "Passwords are not the same")


class LoginForm(forms.Form):
    username = forms.CharField(
        label="username",
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'username',
                'class': 'form-control form-control-lg',
            }
        )
    )

    password = forms.CharField(
        label="password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'password',
                'class': 'form-control form-control-lg',
            }
        )
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password and not authenticate(username=username, password=password):
            raise forms.ValidationError('Wrong credentials')

        return self.cleaned_data


# ─── Admin forms ──────────────────────────────────────────────────────────────

class UserAdminForm(forms.ModelForm):
    """Create user form for admin panel."""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}),
    )

    class Meta:
        model = User
        fields = ('Name', 'LastName', 'UserName', 'Email', 'CompanyId', 'Role', 'Applications', 'IsActive')
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'LastName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'UserName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'CompanyId': forms.Select(attrs={'class': 'form-control'}),
            'Role': forms.Select(attrs={'class': 'form-control'}),
            'Applications': forms.CheckboxSelectMultiple(),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_superadmin:
            self.fields['CompanyId'].queryset = Company.objects.filter(
                id=self.request.user.CompanyId_id
            )
            self.fields.pop('Role')

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned


class UserAdminEditForm(forms.ModelForm):
    """Edit user form (no password change here)."""
    class Meta:
        model = User
        fields = ('Name', 'LastName', 'Email', 'CompanyId', 'Role', 'Applications', 'IsActive')
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'LastName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'CompanyId': forms.Select(attrs={'class': 'form-control'}),
            'Role': forms.Select(attrs={'class': 'form-control'}),
            'Applications': forms.CheckboxSelectMultiple(),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_superadmin:
            self.fields['CompanyId'].queryset = Company.objects.filter(
                id=self.request.user.CompanyId_id
            )


class CompanyAdminForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('CompanyName', 'LocationState', 'LocationCounty', 'CompanyType', 'Logo', 'IsActive')
        widgets = {
            'CompanyName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'LocationState': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'LocationCounty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'CompanyType': forms.Select(attrs={'class': 'form-control'}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
