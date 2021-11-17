from django.shortcuts import render
from django.contrib import messages
from .models import Device
from .forms import UploadFileForm
from shared.inventory.inventory_import import inventory_importer


def device_detailed_info(request, device_id):
    device_info = Device.objects.get(pk=device_id)
    context = {
        'title': 'Device Detailed Information',
        'card_header': 'Device Detailed Information',
        'data': device_info
    }
    return render(request, 'inventory/device_detailed_info.html', context)


def device_inventory(request):
    list_of_devices = Device.objects.all()
    context = {
        'title': 'Inventory - List Devices',
        'card_header': 'Inventory - List Devices',
        'data': list_of_devices,
    }
    return render(request, 'inventory/device_inventory.html', context)


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
        if request.FILES:
            if form.is_valid():
                result = inventory_importer(request.FILES['file'])
                if result['status'] == 'success':
                    messages.success(request, 'Import was successful')
                else:
                    messages.error(request, result)
        else:
            messages.error(request, 'No file was provided...')
        context = {
            'title': 'Inventory - Import Devices',
            'card_header': 'Inventory - Import Devices',
            'form': form
        }
        return render(request, 'inventory/device_inventory_import.html', context)
