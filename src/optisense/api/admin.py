from django.contrib import admin

from .models import Camera, Outlet, Record, CustomUser

admin.site.register(Camera)
admin.site.register(Outlet)
admin.site.register(Record)
admin.site.register(CustomUser)
