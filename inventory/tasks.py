from celery import shared_task
from time import sleep


@shared_task(bind=True, track_started=True)
def task_run_device_discovery(self):
    from .scripts.device_connector import device_run_discovery
    sleep(1)
    task_status = device_run_discovery()
    if task_status['status'] == 'success':
        return task_status
