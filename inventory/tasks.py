from celery import shared_task
from celery.result import AsyncResult
from time import sleep
from housekeeping.models import CeleryJobResults


@shared_task(bind=True, track_started=True)
def task_run_device_discovery(self):
    from .scripts.device_connector import device_run_discovery
    task_status = device_run_discovery()
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