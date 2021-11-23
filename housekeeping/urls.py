from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'housekeeping'
urlpatterns = [
    path(
        '',
        login_required(views.housekeeping_celery_tasks),
        name='housekeeping_celery_tasks'
    ),
]
