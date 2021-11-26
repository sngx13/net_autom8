from django.contrib import admin
from .models import Device, DeviceInterfaces


admin.site.register([Device, DeviceInterfaces])
