from django import forms
from django.core.validators import FileExtensionValidator


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select a file',
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )
