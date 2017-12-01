from django.contrib import admin
from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.apps import apps


# Register your models here.
app = apps.get_app_config('app')
for model_name, model in app.models.items():
    admin.site.register(model)