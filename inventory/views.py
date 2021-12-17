# Pandas
import pandas as pd
# Django
from django.shortcuts import render
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils import timezone
# Other
from random import randint
# Tasks
from .tasks import task_run_device_discovery
from .tasks import task_run_device_rediscovery
# Scripts
from .scripts.device_configurator import edit_interface
# Models
from .models import Device, DeviceInterfaces
from housekeeping.models import CeleryUserJobResults
# Forms
from .forms import UploadFileForm, DeviceCreateForm, DeviceEditForm, InterfaceEditForm


def inventory_importer(file):
    try:
        data = []
        add_random_number = randint(100, 1000)
        uploaded_file = f'uploaded_files/imported_file_{add_random_number}.csv'
        with open(uploaded_file, 'wb+') as csv_file:
            for chunk in file.chunks():
                csv_file.write(chunk)
        df = pd.read_csv(uploaded_file, sep=',')
        for i in range(len(df)):
            data.append(
                Device(
                    hostname=df.iloc[i][0],
                    mgmt_ip=df.iloc[i][1],
                    vendor=df.iloc[i][2],
                    date_added=timezone.now()
                )
            )
        Device.objects.bulk_create(data)
        return {
            'status': 'success',
            'message': 'CSV file imported successfully!'
        }
    except Exception as error:
        return {
            'status': 'fail',
            'message': str(error)
        }


def device_detailed_information(request, device_id):
    device = Device.objects.get(pk=device_id)
    context = {
        'title': 'Device Detailed Information',
        'card_header': f'Information for: {device.hostname} {device.mgmt_ip}',
        'data': {
            'version': device,
            'interfaces': DeviceInterfaces.objects.filter(device_id=device_id)
        }
    }
    return render(
        request,
        'inventory/device_detailed_information.html',
        context
    )


def device_force_rediscovery(request, device_id):
    device = Device.objects.get(pk=device_id)
    task = task_run_device_rediscovery.delay(device_id)
    task_add_to_db = CeleryUserJobResults(
        task_id=task.id,
        task_requested_by=request.user,
        start_time=timezone.now()
    )
    task_add_to_db.save()
    messages.success(
        request,
        f'Rediscovery task added for {device.hostname}: {task.id}')
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
                    username=request.POST['username'],
                    password=request.POST['password'],
                    vendor=request.POST['vendor'],
                    date_added=timezone.now()
                )
                add_device.save()
                task = task_run_device_discovery.delay()
                task_add_to_db = CeleryUserJobResults(
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
                    task_add_to_db = CeleryUserJobResults(
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


def device_interface_edit(request, interface_name):
    interface = DeviceInterfaces.objects.get(name=interface_name)
    context = {
        'title': 'Device - Edit Interface',
        'card_header': f'Device: {interface.device_id.hostname} - Editing Interface: {interface.name}'
    }
    if request.method == 'GET':
        form = InterfaceEditForm(instance=interface)
        context['form'] = form
        return render(request, 'inventory/device_interface_edit.html', context)
    elif request.method == 'POST':
        form = InterfaceEditForm(request.POST, instance=interface)
        context['form'] = form
        if form.is_valid():
            edit_interface(interface.device_id, interface)
            form.save()
            messages.success(
                request,
                f'Changes to: {interface.name} succeeded!'
            )
        else:
            messages.error(
                request,
                'There has been a problem editing the interface!'
            )
        return HttpResponseRedirect(request.path)
    return render(request, 'inventory/device_interface_edit.html', context)


def device_inventory_list(request):
    list_of_devices = Device.objects.all()
    context = {
        'title': 'Inventory - List Devices',
        'card_header': 'Inventory - List Devices',
        'data': list_of_devices,
    }
    return render(request, 'inventory/device_inventory_list.html', context)
