from django.contrib import admin
from .models import CeleryUserJobResults, CeleryBackendJobResults


admin.site.register([CeleryUserJobResults, CeleryBackendJobResults])
