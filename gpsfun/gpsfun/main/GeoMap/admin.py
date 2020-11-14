from django.contrib import admin
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.main.GeoName.models import country_by_code, region_by_code

class GeositeAdmin(admin.ModelAdmin):
    fields = ('code', 'name', 'url', 'cache_url', 'logo', 'enabled')
    list_display = ('code', 'name', 'url', 'cache_url', 'logo', 'enabled')
    

class GeothingAdmin(admin.ModelAdmin):
    fields = ('geosite', 'pid', 'code', 'type_code', 'name', 'author', 
              'created_date', 'country_code', 'admin_code', 'location')
    list_display = ('code', 'pid', 'geosite_code', 'author', 'name',
                    'created_date', 'geothing_location', 'country', 'region')
    
    def geosite_code(self, obj):
        return obj.geosite.code
    
    def country(self, obj):
        return country_by_code(obj.country_code)

    def region(self, obj):
        return region_by_code(obj.country_code, [obj.admin_code])
    
    def geothing_location(self, obj):
        def improve_coordinate(ltuple, suffix, alt):
            if ltuple[0] < 0:
                return [-ltuple[0], ltuple[1], alt]
            else:
                return list(ltuple) + [suffix]
               
        latitude = improve_coordinate(obj.latitude_degree_minutes, 'N', 'S')
        longitude = improve_coordinate(obj.longitude_degree_minutes, 'E', 'W')
        data = latitude + longitude
        return u'{} {:0.3f}{} {} {:0.3f}{}'.format(*data)
    
    geothing_location.short_description = 'Location'
    geosite_code.short_description = 'GeoSite'
        
admin.site.register(Geosite, GeositeAdmin)
admin.site.register(Geothing, GeothingAdmin)
