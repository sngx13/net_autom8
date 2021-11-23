from django.shortcuts import render
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from .models import Device
from .forms import UploadFileForm, DeviceCreateForm
from .scripts.device_bulk_import import inventory_importer
from .scripts.device_connector import device_get_details
from .tasks import task_run_device_discovery
from celery.result import AsyncResult


def device_detailed_info(request, device_id):
    device = Device.objects.get(pk=device_id)
    context = {
        'title': 'Device Detailed Information',
        'card_header': f'Device Detailed Information - {device.hostname} {device.mgmt_ip}',
        'data': device_get_details(device.mgmt_ip, device.vendor)
    }
    return render(request, 'inventory/device_detailed_info.html', context)


def device_delete(request, device_id):
    device_to_delete = Device.objects.get(pk=device_id)
    device_to_delete.delete()
    messages.success(
        request, f'Device: {device_to_delete.hostname} was deleted successfully!'
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def device_create(request):
    if request.method == 'GET':
        form = DeviceCreateForm(request.POST)
        context = {
            'title': 'Inventory - Create Device',
            'card_header': 'Inventory - Create Device',
            'form': form
        }
        return render(request, 'inventory/device_create.html', context)
    elif request.method == 'POST':
        form = DeviceCreateForm(request.POST)
        if form.is_valid():
            try:
                add_device = Device(
                    hostname=request.POST['hostname'],
                    mgmt_ip=request.POST['mgmt_ip'],
                    vendor=request.POST['vendor'],
                    date_added=timezone.now()
                )
                add_device.save()
                task = task_run_device_discovery.delay()
                task_result = AsyncResult(task.id)
                messages.success(
                    request,
                    f'Device added successfully! {task_result.status} discovery: {task.id}'
                )
            except Exception as error:
                messages.error(request, str(error))
        else:
            messages.error(request, 'Invalid information provided!')
        context = {
            'title': 'Inventory - Create Device',
            'card_header': 'Inventory - Create Device',
            'form': form
        }
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def device_inventory_import(request):
    if request.method == 'GET':
        form = UploadFileForm(request.POST, request.FILES)
        context = {
            'title': 'Inventory - Import Devices',
            'card_header': 'Inventory - Import Devices',
            'form': form
        }
        return render(request, 'inventory/device_inventory_import.html', context)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        context = {
            'title': 'Inventory - Import Devices',
            'card_header': 'Inventory - Import Devices',
            'form': form
        }
        if request.FILES:
            if form.is_valid():
                result = inventory_importer(request.FILES['file'])
                if result['status'] == 'success':
                    task = task_run_device_discovery.delay()
                    task_result = AsyncResult(task.id)
                    messages.success(
                        request,
                        f'Import was successful! {task_result.status} discovery: {task.id}')
                else:
                    messages.error(request, result)
            else:
                return render(request, 'inventory/device_inventory_import.html', context)
        else:
            messages.error(request, 'No file was provided!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def device_inventory(request):
    list_of_devices = Device.objects.all()
    context = {
        'title': 'Inventory - List Devices',
        'card_header': 'Inventory - List Devices',
        'data': list_of_devices,
    }
    return render(request, 'inventory/device_inventory.html', context)
