from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'housekeeping'
urlpatterns = [
    path(
        '',
        login_required(views.housekeeping_celery_user_tasks),
        name='housekeeping_celery_user_tasks'
    ),
    path(
        'housekeeping_celery_backend_tasks/',
        login_required(views.housekeeping_celery_backend_tasks),
        name='housekeeping_celery_backend_tasks'
    )
]
