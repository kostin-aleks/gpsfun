from django.urls import path
from gpsfun.geokret.views import (
    map_geokret_info, geokrety_map_change_country,
    geokrety_map_search_waypoint, geokrety_map,
    geokrety_api_who_in_cache, geokrety_map_get_geokrety
)

urlpatterns = [
    path('geokret/info/',
        map_geokret_info, name="map-geokret-info"),
    path('change/country/', geokrety_map_change_country,
        name="geokrety-map-change-country"),
    path('search/waypoint/',
        geokrety_map_search_waypoint,
        name="geokret-map-search-by-waypoint"),
    path('map/', geokrety_map, name="geokrety-map"),
    path('cache/<cache_code>/',
        geokrety_api_who_in_cache,
        name="geokrety-api-in-cache"),
    path('get/geokrety/', geokrety_map_get_geokrety,
        name="geokret-map-get-geokrety"),
]

