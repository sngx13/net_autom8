from datetime import date
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
from inventory.models import Device


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
        task_id = self.request.id
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
                    task_id = self.request.id,
                    task_requested_by = 'periodic_device_poll_script',
                    start_time = timezone.now()
        )
        task_add_to_db.save()
        task_update_db = CeleryBackendJobResults.objects.get(
            task_id = self.request.id
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
            task_id = self.request.id,
            task_name = self.name,
            task_result = {
                'status': 'rejected',
                'details': ['Inventory is empty']
            },
            task_status = 'REJECTED',
            task_requested_by = 'periodic_device_poll_script',
            start_time = timezone.now()
        )
        task_add_to_db.save()
        return {'status': 'rejected', 'details': ['Inventory is empty']}


@shared_task(bind=True, track_started=True)
def task_cleanup_backend_db(self):
    task_result = {}
    progress = []
    date_today = date.today().isoformat()
    if CeleryBackendJobResults.objects.all():
        task_add_to_db = CeleryBackendJobResults(
            task_id=self.request.id,
            task_name = 'task_cleanup_backend_db',
            task_requested_by = 'CRON',
            start_time=timezone.now()
        )
        task_add_to_db.save()
        for task in CeleryBackendJobResults.objects.all():
            if date_today not in str(task.start_time):
                if task.delete():
                    progress.append(
                        f'[+] Deleting: {task.pk} as these are now obsolete'
                    )
            elif date_today in str(task.start_time):
                progress.append(
                    f'[+] Keeping {task.pk} as these contain todays date'
                )
        task_result.update(
            {
                'status': 'success',
                'details': progress,
                'message': 'DB Cleanup completed successfully'
            }
        )
        task_add_to_db.task_status = 'SUCCESS'
        task_add_to_db.task_result = task_result
        self.update_state(state=states.SUCCESS, meta=task_result)
        task_add_to_db.save()
        return task_result
    else:
        task_add_to_db = CeleryBackendJobResults(
            task_id = self.request.id,
            task_name = task_cleanup_backend_db,
            task_result = {
                'status': 'rejected',
                'details': ['CeleryBackendJobResultsDB does not exist']
            },
            task_status = 'REJECTED',
            task_requested_by = 'Periodic CRON task',
            start_time = timezone.now()
        )
        task_add_to_db.save()
        return {'status': 'rejected', 'details': ['CeleryBackendJobResultsDB does not exist']}