from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.html import mark_safe
from .models import Device


VENDORS = (
    ('', '--- Select ---'),
    ('Cisco', 'Cisco'),
    ('Juniper', 'Juniper'),
    ('Nokia', 'Nokia'),
)


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='',
        widget=forms.FileInput(
            attrs={'class': 'form-control form-control-sm'}
        ),
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )


class DeviceCreateForm(forms.Form):
    hostname = forms.CharField(
        label=mark_safe('<i class="fas fa-signature"></i> Hostname'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    mgmt_ip = forms.CharField(
        label=mark_safe('<i class="fas fa-at"></i> MGMT IP'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    vendor = forms.ChoiceField(
        label=mark_safe('<i class="fas fa-briefcase"></i> Vendor'),
        widget=forms.Select(attrs={'class': 'form-control form-select-sm'}),
        choices=VENDORS
    )
    username = forms.CharField(
        label=mark_safe('<i class="fas fa-users-cog"></i> Username'),
        widget=forms.TextInput(
            attrs={'class': 'form-control form-control-sm', 'placeholder': 'Optional field'}
        ),
        required=False
    )
    password = forms.CharField(
        label=mark_safe('<i class="fas fa-key"></i> Password'),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-sm', 'placeholder': 'Optional field'}
        ),
        required=False
    )


class DeviceEditForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ('hostname', 'mgmt_ip', 'username', 'password')
        labels = {
            'hostname': mark_safe('<i class="fas fa-signature"></i> Hostname'),
            'mgmt_ip': mark_safe('<i class="fas fa-at"></i> MGMT IP'),
            'username': mark_safe('<i class="fas fa-users-cog"></i> Username'),
            'password': mark_safe('<i class="fas fa-key"></i> Password')

        }
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'mgmt_ip': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-sm'})
        }
