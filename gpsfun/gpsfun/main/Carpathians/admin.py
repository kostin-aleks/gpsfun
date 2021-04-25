from django.contrib import admin
from django.contrib.auth.models import User
from gpsfun.main.Carpathians.models import Ridge

class RidgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'map_image')

admin.site.register(Ridge, RidgeAdmin)

