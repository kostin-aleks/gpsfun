"""
There are Admin Classes to present in admin interface objects
related to GeoKrety
"""

from django.contrib import admin
from gpsfun.main.GeoKrety.models import GeoKret


class GeoKretAdmin(admin.ModelAdmin):
    """ GeoKretAdmin """
    list_display = (
        'name', 'location', 'gkid', 'waypoint', 'type_code', 'distance',
        'owner_id', 'state', 'image', 'country_code', 'admin_code'
    )
    search_fields = ('name',)
    ordering = ('-id',)
    raw_id_fields = ('location',)

admin.site.register(GeoKret, GeoKretAdmin)
