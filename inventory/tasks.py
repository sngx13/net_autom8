# Django
from django.utils import timezone
# Celery
from celery import shared_task, states
from celery.result import AsyncResult
# Scrips
from .scripts.device_discovery import device_initiate_discovery
from .scripts.device_poller import device_initiate_poller
# Models
from housekeeping.models import CeleryUserJobResults
from housekeeping.models import CeleryBackendJobResults
from .models import Device


@shared_task(bind=True, track_started=True)
def task_run_device_discovery(self):
    run_task = device_initiate_discovery()
    task_update_db = CeleryUserJobResults.objects.get(
        task_id=self.request.id
    )
    task_update_db.task_name = self.name
    task_result = AsyncResult(self.request.id)
    if run_task['status'] == 'success':
        self.update_state(state=states.SUCCESS, meta=run_task)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    else:
        self.update_state(state=states.FAILURE)
        task_update_db.task_result = run_task
        task_update_db.task_status = 'FAILURE'
        task_update_db.save()
    return run_task


@shared_task(bind=True, track_started=True)
def task_run_device_rediscovery(self, device_id):
    run_task = device_initiate_discovery(device_id)
    task_update_db = CeleryUserJobResults.objects.get(
        task_id=self.request.id
    )
    task_update_db.task_name = self.name
    task_result = AsyncResult(self.request.id)
    if run_task['status'] == 'success':
        self.update_state(state=states.SUCCESS, meta=run_task)
        task_update_db.task_result = task_result.info
        task_update_db.task_status = task_result.status
        task_update_db.save()
    else:
        self.update_state(state=states.FAILURE)
        task_update_db.task_result = run_task
        task_update_db.task_status = 'FAILURE'
        task_update_db.save()
    return run_task


@shared_task(bind=True, track_started=True)
def task_periodic_device_poll(self):
    if Device.objects.all():
        run_task = device_initiate_poller()
        task_add_to_db = CeleryBackendJobResults(
                    task_id=self.request.id,
                    task_requested_by='periodic_device_poll_script',
                    start_time=timezone.now()
        )
        task_add_to_db.save()
        task_update_db = CeleryBackendJobResults.objects.get(
            task_id=self.request.id
        )
        task_update_db.task_name = self.name
        task_result = AsyncResult(self.request.id)
        if run_task['status'] == 'success':
            self.update_state(state=states.SUCCESS, meta=run_task)
            task_update_db.task_result = task_result.info
            task_update_db.task_status = task_result.status
            task_update_db.save()
        else:
            self.update_state(state=states.FAILURE)
            task_update_db.task_result = run_task
            task_update_db.task_status = 'FAILURE'
            task_update_db.save()
        return run_task
    else:
        task_add_to_db = CeleryBackendJobResults(
            task_id=self.request.id,
            task_name=self.name,
            task_result={
                'status': 'rejected',
                'details': ['Inventory is empty']
            },
            task_status='REJECTED',
            task_requested_by='periodic_device_poll_script',
            start_time=timezone.now()
        )
        task_add_to_db.save()
        return {'status': 'rejected', 'details': ['Inventory is empty']}
