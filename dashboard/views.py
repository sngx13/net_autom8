from django.shortcuts import render
from inventory.models import Device


def device_graphing_data():
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
            }
        }
    for device in Device.objects.all():
        data['inventory_chart']['rows'].append(
                {'c': [{'v': device.hostname}, {'v': 1}]}
        )
    data['device_list_chart']['rows'].append(
        {'c': [{'v': 'a'}, {'v': len(Device.objects.all())}]}
    )
    return data


def dashboard(request):
    context = {
        'title': 'Dashboard',
        'card_header': 'Dashboard',
        'data': device_graphing_data()
    }
    return render(request, 'dashboard/dashboard.html', context)
