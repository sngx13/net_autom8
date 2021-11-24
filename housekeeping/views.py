from django.shortcuts import render
from celery import current_app
from .models import CeleryJobResults


def housekeeping_celery_tasks(request):
    tasks = current_app.control.inspect(['celery@django'])
    context = {
        'title': 'Housekeeping - Celery Tasks',
        'card_header': 'Housekeeping - Celery Tasks',
        'data': {
            'celery_statistics': tasks.stats(),
            'registered_tasks': tasks.registered_tasks(),
            'scheduled_tasks': tasks.scheduled(),
            'active_tasks': tasks.active(),
            'reserved_tasks': tasks.reserved(),
            'tasks_list': CeleryJobResults.objects.all()
        }
    }
    return render(
        request,
        'housekeeping/housekeeping_celery_tasks.html',
        context
    )
