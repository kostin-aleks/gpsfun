from django.contrib import admin
from django.contrib.auth.models import User
from gpsfun.main.User.models import GPSFunUser

class GPSFunUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name',
                    'geocity', 'gcsu_username')

admin.site.register(GPSFunUser, GPSFunUserAdmin)

