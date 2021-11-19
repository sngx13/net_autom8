import json
from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.html import mark_safe
from static.files.uk_cities_list import cities


VENDORS = (
    ('', '--->Select<---'),
    ('Cisco', 'Cisco'),
    ('Juniper', 'Juniper'),
    ('Nokia', 'Nokia'),
)


def location_choices():
    locations_list = [('', '--->Select<---')]
    for city in cities:
        locations_list.append((city['city'], city['city']))
    return tuple(locations_list)


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
    software_version = forms.CharField(
        label=mark_safe('<i class="fas fa-code-branch"></i> Software'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    serial_number = forms.CharField(
        label=mark_safe('<i class="fas fa-barcode"></i> Serial'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    vendor = forms.ChoiceField(
        label=mark_safe('<i class="fas fa-briefcase"></i> Vendor'),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        choices=VENDORS
    )
    hardware_model = forms.CharField(
        label=mark_safe('<i class="fas fa-sitemap"></i> Model'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    location = forms.ChoiceField(
        label=mark_safe('<i class="fas fa-search-location"></i> Location'),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        choices=location_choices()
    )
