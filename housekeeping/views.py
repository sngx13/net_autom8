# Django
from django.shortcuts import render
# Celery
from celery import current_app
from celery.utils.nodenames import gethostname
# Models
from .models import CeleryUserJobResults, CeleryBackendJobResults


hostname = 'celery@' + str(gethostname())
tasks = current_app.control.inspect([hostname])


def housekeeping_celery_user_tasks(request):
    tasks_list = CeleryUserJobResults.objects.all().order_by('-start_time')
    context = {
            'title': 'Housekeeping - Celery User Tasks',
            'card_header': 'Housekeeping - User Celery Tasks',
            'data': {
                'tasks_list': tasks_list
            }
        }
    if tasks.stats():
        data = {
            'celery_information': {
                'celery_statistics': tasks.stats(),
                'registered_tasks': tasks.registered_tasks()[hostname],
                'scheduled_tasks': tasks.scheduled()[hostname],
                'active_tasks': tasks.active()[hostname],
                'reserved_tasks': tasks.reserved()
            }
        }
        context['data'].update(data)
        return render(
            request,
            'housekeeping/housekeeping_celery_user_tasks.html',
            context
        )
    else:
        return render(
                request,
                'housekeeping/housekeeping_celery_user_tasks.html',
                context
            )


def housekeeping_celery_backend_tasks(request):
    tasks_list = CeleryBackendJobResults.objects.all().order_by('-start_time')
    context = {
            'title': 'Housekeeping - Celery Backend Tasks',
            'card_header': 'Housekeeping - Celery Backend Tasks',
            'data': {
                'tasks_list': tasks_list
            }
        }
    if tasks.stats():
        data = {
            'celery_information': {
                'celery_statistics': tasks.stats(),
                'registered_tasks': tasks.registered_tasks()[hostname],
                'scheduled_tasks': tasks.scheduled()[hostname],
                'active_tasks': tasks.active()[hostname],
                'reserved_tasks': tasks.reserved()
            }
        }
        context['data'].update(data)
        return render(
            request,
            'housekeeping/housekeeping_celery_backend_tasks.html',
            context
        )
    else:
        return render(
                request,
                'housekeeping/housekeeping_celery_backend_tasks.html',
                context
            )
