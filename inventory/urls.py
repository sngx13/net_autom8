from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'inventory'
urlpatterns = [
    path(
        'device_inventory_list/',
        login_required(views.device_inventory_list),
        name='device_inventory_list'
    ),
    path(
        'device_detailed_information/<device_id>/',
        login_required(views.device_detailed_information),
        name='device_detailed_information'
    ),
    path(
        'device_force_rediscovery/<device_id>/',
        login_required(views.device_force_rediscovery),
        name='device_force_rediscovery'
    ),
    path(
        'device_inventory_edit/<device_id>/',
        login_required(views.device_inventory_edit),
        name='device_inventory_edit'
    ),
    path(
        'device_interface_edit/<interface_name>/',
        login_required(views.device_interface_edit),
        name='device_interface_edit'
    ),
    path(
        'device_interface_delete/<interface_name>/',
        login_required(views.device_interface_delete),
        name='device_interface_delete'
    ),
    path(
        'device_inventory_import/',
        login_required(views.device_inventory_import),
        name='device_inventory_import'
    ),
    path(
        'device_inventory_create/',
        login_required(views.device_inventory_create),
        name='device_inventory_create'
    ),
    path(
        'device_inventory_delete/<device_id>/',
        login_required(views.device_inventory_delete),
        name='device_inventory_delete'
    ),
    path(
        'device_run_command',
        login_required(views.device_run_command),
        name='device_run_command'
    )
]
