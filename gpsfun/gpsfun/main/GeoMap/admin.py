"""
Admin classes for models from GeoMap
"""
from django.contrib import admin
from gpsfun.main.GeoMap.models import Geothing, Geosite
from gpsfun.main.GeoName.models import country_by_code, region_by_code


class GeositeAdmin(admin.ModelAdmin):
    """ GeositeAdmin """
    fields = ('code', 'name', 'url', 'cache_url', 'logo', 'enabled')
    list_display = ('code', 'name', 'url', 'cache_url', 'logo', 'enabled')


class GeothingAdmin(admin.ModelAdmin):
    """ GeothingAdmin """
    fields = ('geosite', 'pid', 'code', 'type_code', 'name', 'author',
              'created_date', 'country_code', 'admin_code', 'location')
    list_display = ('code', 'pid', 'geosite_code', 'author', 'name',
                    'created_date', 'geothing_location', 'country', 'region')

    def geosite_code(self, obj):
        """ render geosite code """
        return obj.geosite.code

    def country(self, obj):
        """ render country """
        return country_by_code(obj.country_code)

    def region(self, obj):
        """ render region """
        return region_by_code(obj.country_code, [obj.admin_code])

    def geothing_location(self, obj):
        """ render geothing location """
        def improve_coordinate(ltuple, suffix, alt):
            """ improve coordinate """
            if ltuple[0] < 0:
                return [-ltuple[0], ltuple[1], alt]

            return list(ltuple) + [suffix]

        latitude = improve_coordinate(obj.latitude_degree_minutes, 'N', 'S')
        longitude = improve_coordinate(obj.longitude_degree_minutes, 'E', 'W')
        data = latitude + longitude
        return '{} {:0.3f}{} {} {:0.3f}{}'.format(*data)

    geothing_location.short_description = 'Location'
    geosite_code.short_description = 'GeoSite'

admin.site.register(Geosite, GeositeAdmin)
admin.site.register(Geothing, GeothingAdmin)
