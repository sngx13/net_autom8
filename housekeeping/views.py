from django.shortcuts import render
from celery import current_app
from celery.utils.nodenames import gethostname
from .models import CeleryJobResults


def housekeeping_celery_tasks(request):
    hostname = 'celery@' + str(gethostname())
    tasks = current_app.control.inspect([hostname])
    tasks_list = CeleryJobResults.objects.all().order_by('-start_time')
    context = {
            'title': 'Housekeeping - Celery Tasks',
            'card_header': 'Housekeeping - Celery Tasks',
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
            'housekeeping/housekeeping_celery_tasks.html',
            context
        )
    else:
        return render(
                request,
                'housekeeping/housekeeping_celery_tasks.html',
                context
            )
