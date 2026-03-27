from django.contrib import admin
from .models import *
from .models import CustomUser

admin.site.register(CustomUser)
admin.site.register(Location)
admin.site.register(Fund)
admin.site.register(Project)
admin.site.register(Proof)
admin.site.register(Complaint)