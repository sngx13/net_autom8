# Django
from django.utils import timezone
# Celery
from celery import shared_task, states
from celery.result import AsyncResult
# Scrips
from .scripts.device_discovery import device_initiate_discovery
from .scripts.device_poller import device_initiate_poller
# Models
from housekeeping.models import CeleryJobResults
from .models import Device


@shared_task(bind=True, track_started=True)
def task_run_device_discovery(self):
    task_status = device_initiate_discovery()
    task_update_db = CeleryJobResults.objects.get(task_id=self.request.id)
    task_update_db.task_name = self.name
    task_result = AsyncResult(self.request.id)
    if task_status['status'] == 'success':
        self.update_state(state=states.SUCCESS, meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    else:
        self.update_state(state=states.FAILURE, meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    return task_status


@shared_task(bind=True, track_started=True)
def task_run_device_rediscovery(self, device_id):
    task_status = device_initiate_discovery(device_id)
    task_update_db = CeleryJobResults.objects.get(task_id=self.request.id)
    task_update_db.task_name = self.name
    task_result = AsyncResult(self.request.id)
    if task_status['status'] == 'success':
        self.update_state(state=states.SUCCESS, meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    else:
        self.update_state(state=states.FAILURE, meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    return task_status


@shared_task(bind=True, track_started=True)
def task_periodic_device_poll(self):
    if Device.objects.all():
        for device in Device.objects.all():
            task_status = device_initiate_poller(device.id)
        task_add_to_db = CeleryJobResults(
                    task_id=self.request.id,
                    task_requested_by='periodic_device_poll_script',
                    start_time=timezone.now()
        )
        task_add_to_db.save()
        task_update_db = CeleryJobResults.objects.get(task_id=self.request.id)
        task_update_db.task_name = self.name
        task_result = AsyncResult(self.request.id)
        if task_status['status'] == 'success':
            self.update_state(state=states.SUCCESS, meta=task_status)
            task_update_db.task_result = task_result.info
            task_update_db.task_status = task_result.status
            task_update_db.save()
        else:
            self.update_state(state=states.FAILURE, meta=task_status)
            task_update_db.task_result = task_result.info
            task_update_db.task_status = task_result.status
            task_update_db.save()
        return task_status
