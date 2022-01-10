# Django
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
# Forms
from .forms import SignUpForm


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
        'data': User.objects.all()
    }
    return render(request, 'registration/login_history.html', context)
