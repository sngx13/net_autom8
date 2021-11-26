from django.db import models
from django.utils import timezone


class Device(models.Model):
    hostname = models.CharField(unique=True, max_length=255)
    mgmt_ip = models.GenericIPAddressField(unique=True, max_length=12)
    username = models.CharField(blank=True, max_length=255, null=True)
    password = models.CharField(blank=True, max_length=255, null=True)
    software_version = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    vendor = models.CharField(max_length=255)
    hardware_model = models.CharField(max_length=255)
    rest_conf_enabled = models.BooleanField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now())


class DeviceInterfaces(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    speed = models.CharField(max_length=255)
    duplex = models.CharField(max_length=255)
    mac_addr = models.CharField(max_length=255)
