from django.shortcuts import render
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from housekeeping.models import CeleryJobResults
from .scripts.device_bulk_import import inventory_importer
from .scripts.device_connector import device_get_details_via_ssh
from .scripts.device_connector import device_get_details_via_rest
from .tasks import task_run_device_discovery
from .models import Device, DeviceInterfaces
from .forms import UploadFileForm, DeviceCreateForm, DeviceEditForm


def device_detailed_information(request, device_id):
    device = Device.objects.get(pk=device_id)
    context = {
        'title': 'Device Detailed Information',
        'card_header': f'Device Detailed Information - {device.hostname} {device.mgmt_ip}',
    }
    if device.rest_conf_enabled:
        device_get_details_via_rest(device_id)
        data = DeviceInterfaces.objects.filter(device_id=device_id)
        context['data'] = {'restconf': data}
    if not device.rest_conf_enabled:
        context['data'] = {'ssh_cli': device_get_details_via_ssh(device_id)}
    return render(
        request,
        'inventory/device_detailed_information.html',
        context
    )


def device_inventory_force_discovery(request):
    task = task_run_device_discovery.delay()
    task_add_to_db = CeleryJobResults(
        task_id=task.id,
        task_requested_by=request.user,
        start_time=timezone.now()
    )
    task_add_to_db.save()
    messages.success(
        request,
        f'Creating discovery task: {task.id}'
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def device_inventory_delete(request, device_id):
    device = Device.objects.get(pk=device_id)
    device.delete()
    messages.success(
        request,
        f'Device: {device.hostname} was deleted successfully!'
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def device_inventory_create(request):
    form = DeviceCreateForm(request.POST)
    context = {
        'title': 'Inventory - Create Device',
        'card_header': 'Inventory - Create Device',
        'form': form
    }
    if request.method == 'GET':
        return render(
            request,
            'inventory/device_inventory_create.html',
            context
        )
    elif request.method == 'POST':
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
                task_add_to_db = CeleryJobResults(
                    task_id=task.id,
                    task_requested_by=request.user,
                    start_time=timezone.now()
                )
                task_add_to_db.save()
                messages.success(
                    request,
                    f'Device added successfully! Pending discovery: {task.id}'
                )
            except Exception as error:
                messages.error(request, str(error))
        else:
            messages.error(
                request,
                'Invalid information provided!'
            )
        return HttpResponseRedirect(request.path)


def device_inventory_import(request):
    form = UploadFileForm(request.POST, request.FILES)
    context = {
        'title': 'Inventory - Import Devices',
        'card_header': 'Inventory - Import Devices',
        'form': form
    }
    if request.method == 'GET':
        return render(
            request,
            'inventory/device_inventory_import.html',
            context
        )
    if request.method == 'POST':
        if request.FILES:
            if form.is_valid():
                result = inventory_importer(request.FILES['file'])
                if result['status'] == 'success':
                    task = task_run_device_discovery.delay()
                    task_add_to_db = CeleryJobResults(
                        task_id=task.id,
                        task_requested_by=request.user,
                        start_time=timezone.now()
                    )
                    task_add_to_db.save()
                    messages.success(
                        request,
                        f'Import was successful! Pending discovery: {task.id}')
                else:
                    messages.error(request, result)
            else:
                return render(
                    request,
                    'inventory/device_inventory_import.html',
                    context
                )
        else:
            messages.error(request, 'No file was provided!')
        return HttpResponseRedirect(request.path)


def device_inventory_edit(request, device_id):
    device = Device.objects.get(pk=device_id)
    context = {
            'title': 'Inventory - Device Editor',
            'card_header': f'Device Editor: {device.hostname} {device.mgmt_ip}',
            'data': device
    }
    if request.method == 'GET':
        form = DeviceEditForm(instance=device)
        context['form'] = form
        return render(request, 'inventory/device_inventory_edit.html', context)
    elif request.method == 'POST':
        form = DeviceEditForm(request.POST, instance=device)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Changes to: {device.hostname} succeeded!'
            )
        else:
            messages.error(
                request,
                'There has been a problem editing the device!'
            )
        return HttpResponseRedirect(request.path)


def device_inventory_list(request):
    list_of_devices = Device.objects.all()
    context = {
        'title': 'Inventory - List Devices',
        'card_header': 'Inventory - List Devices',
        'data': list_of_devices,
    }
    return render(request, 'inventory/device_inventory_list.html', context)
