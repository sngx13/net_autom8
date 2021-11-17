from django.db import models
from django.utils import timezone


class Device(models.Model):
    hostname = models.CharField(unique=True, max_length=255)
    mgmt_ip = models.CharField(unique=True, max_length=12)
    software_version = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    hardware_model = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date_added = models.DateTimeField(default=timezone.now())
