from django.contrib import admin
from hdg.djangoapps.admintable.models import AdminTableConfig

class AdminTableConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'url', 'is_public')

admin.site.register(AdminTableConfig, AdminTableConfigAdmin)
