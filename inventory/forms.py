from django import forms
from django.core.validators import FileExtensionValidator


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select a file',
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )


class DeviceCreateForm(forms.Form):
    hostname = forms.CharField()
    mgmt_ip = forms.CharField()
    software_version = forms.CharField()
    serial_number = forms.CharField()
    vendor = forms.CharField()
    hardware_model = forms.CharField()
    location = forms.CharField()
