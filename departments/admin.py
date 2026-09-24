from django.contrib import admin
from .models import Department, District
admin.site.register([Department, District])
