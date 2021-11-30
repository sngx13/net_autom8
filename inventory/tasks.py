from celery import shared_task
from celery.result import AsyncResult
from time import sleep
from housekeeping.models import CeleryJobResults
from .scripts.device_connector import device_initiate_discovery


@shared_task(bind=True, track_started=True)
def task_run_device_discovery(self):
    task_status = device_initiate_discovery()
    task_update_db = CeleryJobResults.objects.get(task_id=self.request.id)
    task_update_db.task_name = self.name
    task_result = AsyncResult(self.request.id)
    if task_status['status'] == 'success':
        self.update_state(state='COMPLETED', meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    else:
        self.update_state(state='FAILED', meta=task_status)
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
        self.update_state(state='COMPLETED', meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    else:
        self.update_state(state='FAILED', meta=task_status)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    return task_status
