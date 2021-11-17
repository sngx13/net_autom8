from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required, permission_required


urlpatterns = [
    path('dashboard/', include('dashboard.urls')),
    path('inventory/', include('inventory.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path(
        '',
        login_required(
            TemplateView.as_view(template_name='registration/profile.html')
        ),
        name='profile'
    )
]
