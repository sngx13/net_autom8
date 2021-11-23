from django.shortcuts import render
from celery import current_app


def housekeeping_celery_tasks(request):
    tasks = current_app.control.inspect(['celery@django'])
    context = {
        'title': 'Housekeeping - Celery Tasks',
        'card_header': 'Housekeeping - Celery Tasks',
        'data': {
            'registered_tasks': tasks.registered_tasks(),
            'scheduled_tasks': tasks.scheduled(),
            'active_tasks': tasks.active(),
            'reserved_tasks': tasks.reserved()
        }
    }
    return render(request, 'housekeeping/housekeeping_celery_tasks.html', context)
