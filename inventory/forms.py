from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.html import mark_safe


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='',
        widget=forms.FileInput(
            attrs={'class': 'form-control form-control-sm'}
        ),
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )


VENDORS = (
    ('', '--- Select ---'),
    ('Cisco', 'Cisco'),
    ('Juniper', 'Juniper'),
    ('Nokia', 'Nokia'),
)


class DeviceCreateForm(forms.Form):
    hostname = forms.CharField(
        label= mark_safe('<i class="fas fa-signature"></i> Hostname'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    mgmt_ip = forms.CharField(
        label= mark_safe('<i class="fas fa-at"></i> MGMT IP'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    software_version = forms.CharField(
        label= mark_safe('<i class="fas fa-code-branch"></i> Software'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    serial_number = forms.CharField(
        label= mark_safe('<i class="fas fa-barcode"></i> Serial'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    vendor = forms.ChoiceField(
        label= mark_safe('<i class="fas fa-briefcase"></i> Vendor'),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        choices=VENDORS
    )
    hardware_model = forms.CharField(
        label= mark_safe('<i class="fas fa-sitemap"></i> Model'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    location = forms.CharField(
        label= mark_safe('<i class="fas fa-search-location"></i> Location'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
