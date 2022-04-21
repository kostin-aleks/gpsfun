"""
There are Admin Classes to present in admin interface objects related to Country
"""

from django.contrib import admin
from gpsfun.main.GeoName.models import (GeoCity,)


class GeoCityAdmin(admin.ModelAdmin):
    """
    An GeoCityAdmin object encapsulates an instance of the GeoCity
    """
    list_display = (
        'geonameid', 'name', 'asciiname', 'latitude', 'longitude',
        'country', 'admin1', 'admin2', 'admin3', 'population',
        'elevation')
    search_fields = ('name', 'asciiname')
    ordering = ('id', )


admin.site.register(GeoCity, GeoCityAdmin)
