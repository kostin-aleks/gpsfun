"""
There are Admin Classes to present in admin interface objects related to User
"""
from django.contrib import admin
from gpsfun.main.User.models import GPSFunUser

class GPSFunUserAdmin(admin.ModelAdmin):
    """ GPSFunUserAdmin """
    list_display = (
        'user', 'middle_name', 'geocity', 'gcsu_username')

admin.site.register(GPSFunUser, GPSFunUserAdmin)
