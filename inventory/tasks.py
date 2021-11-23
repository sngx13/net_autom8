from celery import shared_task


@shared_task(bind=True, track_started=True)
def task_run_device_discovery(self):
    from .scripts.inventory_device_connector import device_run_discovery
    self.update_state(state='Device discovery starting...')
    task_status = device_run_discovery()
    if task_status['status'] == 'success':
        self.update_state(state='Device discovery has completed successfully')
        return task_status
