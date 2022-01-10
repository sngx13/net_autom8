from django.db import models
from django.utils import timezone


class ExternalVisitorsInfo(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, blank=True, null=True)
    hostname = models.CharField(blank=True, null=True, max_length=255)
    provider = models.CharField(blank=True, null=True, max_length=255)
    bgp_asn = models.CharField(blank=True, null=True, max_length=255)
    city = models.CharField(blank=True, null=True, max_length=255)
    country_code = models.CharField(blank=True, null=True, max_length=2)
    recent_abuse = models.BooleanField(blank=True, null=True)
    fraud_score = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now())