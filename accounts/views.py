import requests
from ipaddress import ip_address
from datetime import datetime
# Django
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
# Forms
from .forms import SignUpForm


def get_today_visitors():
    data = {}
    ip_addr_list = []
    today = str(datetime.now().strftime('%d-%b-%Y'))
    with open('/var/log/nginx/access.log', 'r') as logfile:
        lines = logfile.readlines()
        for line in lines:
            ip_addr = line.split()[0]
            timestamp = line.split()[3].strip('[]').replace('/', '-')
            if ip_address(ip_addr).is_global:
                if today in timestamp:
                    ip_addr_list.append(ip_addr)
    unique_ip_list = set(list(ip_addr_list))
    for ip in unique_ip_list:
        get_geo_info = requests.get(
            f'https://stat.ripe.net/data/maxmind-geo-lite/data.json?resource={ip}'
        )
        if get_geo_info.status_code == 200:
            data.update(
                {
                    ip:get_geo_info.json()['data']['located_resources'][0]['locations'][0]['country']
                }
            )
    return data


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            messages.success(
                request, f'User {user} created successfully, you may now login'
            )
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_history(request):
    context = {
        'title': 'Authentication History',
        'card_header': 'Authentication History',
        'data': User.objects.all(),
        'visitors': get_today_visitors()
    }
    return render(request, 'registration/login_history.html', context)
