from django.db import models
from django.utils import timezone


class Device(models.Model):
    hostname = models.CharField(unique=True, max_length=255)
    mgmt_ip = models.GenericIPAddressField(unique=True, max_length=12)
    username = models.CharField(blank=True, null=True, max_length=255)
    password = models.CharField(blank=True, null=True, max_length=255)
    software_version = models.CharField(blank=True, null=True, max_length=255)
    serial_number = models.CharField(blank=True, null=True, max_length=255)
    vendor = models.CharField(max_length=255)
    hardware_model = models.CharField(blank=True, null=True, max_length=255)
    rest_conf_enabled = models.BooleanField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now())


class DeviceInterfaces(models.Model):
    device_id = models.ForeignKey(Device, null=True, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=255)
    interface_type = models.CharField(blank=True, null=True, max_length=255)
    description = models.CharField(blank=True, null=True, max_length=255)
    ipv4_address = models.GenericIPAddressField(blank=True, null=True, max_length=12)
    ipv4_subnet_mask = models.CharField(blank=True, null=True, max_length=12)
    speed = models.CharField(blank=True, null=True, max_length=255)
    duplex = models.CharField(blank=True, null=True, max_length=255)
    admin_status = models.CharField(blank=True, null=True, max_length=255)
    oper_status = models.CharField(blank=True, null=True, max_length=255)
    phys_address = models.CharField(blank=True, null=True, max_length=255)
    mtu = models.CharField(blank=True, null=True, max_length=5)
    in_crc_errors = models.CharField(blank=True, null=True, max_length=255)
