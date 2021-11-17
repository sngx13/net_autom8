import pandas as pd
import random
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import Device
from .forms import UploadFileForm


def import_inventory(file):
    try:
        data = []
        add_random_number = random.randint(100, 1000)
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
                    software_version=df.iloc[i][2],
                    serial_number=df.iloc[i][3],
                    hardware_model=df.iloc[i][4],
                    location=df.iloc[i][5],
                    date_added=timezone.now()
                )
            )
        Device.objects.bulk_create(data)
        return {'status': 'success'}
    except Exception as error:
        return {'status': 'fail', 'message': str(error)}


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
        if form.is_valid():
            result = import_inventory(request.FILES['file'])
            if result['status'] == 'success':
                messages.success(request, 'Import was successful')
            else:
                messages.error(request, result)
        context = {
            'title': 'Inventory - Import Devices',
            'card_header': 'Inventory - Import Devices',
            'form': form
        }
        return render(request, 'inventory/device_inventory_import.html', context)
