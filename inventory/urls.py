from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'inventory'
urlpatterns = [
    path('device_inventory', login_required(views.device_inventory), name='device_inventory'),
    path('device_inventory_import', login_required(views.device_inventory_import), name='device_inventory_import')
]
