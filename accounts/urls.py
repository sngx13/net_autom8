from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login_history/', views.login_history, name='login_history'),
    path('security_log/', views.security_log, name='security_log')
]
