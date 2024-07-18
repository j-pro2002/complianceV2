from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Complaint)
admin.site.register(Recommendation)
admin.site.register(Report)
admin.site.register(Notification)