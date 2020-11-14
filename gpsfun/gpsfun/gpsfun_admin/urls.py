from django.conf.urls import *
from gpsfun.gpsfun_admin.views import (
    index, last_updates, data_updating_log)


urlpatterns = [
    url(r'^$', index, name="gpsfun-admin-index"),
    url(r'^last_updates/$', last_updates,
        name="gpsfun-admin-last-updates"),
    url(r'^data_updating_log/$', data_updating_log,
        name="gpsfun-admin-updating-log"),
    #url(r'^geokret/info/$', "map_geokret_info", name="map-geokret-info"),
    #url(r'^change/country/$', "geokrety_map_change_country", name="geokrety-map-change-country"),
    ##url(r'^region/caches/$', "geokrety_map_region_caches", name="geokrety-map-region-caches"),
    #url(r'^map/$', 'geokrety_map', name="geokrety-map"),
    #url(r'^cache/(?P<cache_code>\w+)/$', 'geokrety_api_who_in_cache', name="geokrety-api-in-cache"),
]
