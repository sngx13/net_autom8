from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login_history/', views.login_history, name='login_history'),
    path('get_today_visitors/', views.get_today_visitors, name='get_today_visitors')
]
