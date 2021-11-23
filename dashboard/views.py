from django.shortcuts import render
from inventory.models import Device


def device_graphing_data():
    hw_models = []
    data = {
            'inventory_chart': {
                'cols': [
                    {'label': 'Hostname', 'type': 'string'},
                    {'label': 'Count', 'type': 'number'}
                ],
                'rows': []
            },
            'device_list_chart': {
                'cols': [
                    {'label': 'Devices', 'type': 'string'},
                    {'label': 'Count', 'type': 'number'}
                ],
                'rows': []
            },
            'device_models_chart': {
                'cols': [
                    {'label': 'HW Model', 'type': 'string'},
                    {'label': 'Count', 'type': 'number'}
                ],
                'rows': []
            }
        }
    for device in Device.objects.all():
        hw_models.append(device.vendor + ' ' + device.hardware_model)
        data['inventory_chart']['rows'].append(
                {'c': [{'v': device.hostname}, {'v': 1}]}
        )
    unique_models = list(set(hw_models))
    for model in unique_models:
        data['device_models_chart']['rows'].append(
            {'c': [{'v': model}, {'v': hw_models.count(model)}]}
        )
    data['device_list_chart']['rows'].append(
        {'c': [{'v': 'Total Devices'}, {'v': len(Device.objects.all())}]}
    )
    return data


def dashboard(request):
    context = {
        'title': 'Dashboard',
        'card_header': 'Dashboard',
        'data': device_graphing_data()
    }
    return render(request, 'dashboard/dashboard.html', context)
