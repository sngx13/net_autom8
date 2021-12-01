import uuid
from django.db import models


class CeleryJobResults(models.Model):
    task_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        max_length=255
    )
    task_name = models.CharField(max_length=255)
    task_status = models.CharField(max_length=255)
    task_result = models.JSONField(null=True)
    task_requested_by = models.CharField(max_length=255)
    start_time = models.DateTimeField()
