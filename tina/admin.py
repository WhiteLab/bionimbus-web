from django.contrib import admin
from tina.models import *
from django.apps import apps
from django.conf import settings

# Register your models here.
for model in apps.get_app_config(settings.STRINGS['installed_app_name']).models.values():
    admin.site.register(model)
