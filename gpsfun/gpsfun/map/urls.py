"""
urls for application map
"""

from django.urls import path
from gpsfun.map.views import (
    map_import_caches_wpt, map_import_caches_wpt_translit,
    map_cache_info, map_rectangle_things, caches_map,
    map_show_types, map_search_waypoint
)

urlpatterns = [
    path('caches/import/wpt/', map_import_caches_wpt,
         name="map-import-caches-wpt"),
    path('caches/import/wpt/translit/', map_import_caches_wpt_translit,
         name="map-import-caches-wpt-translit"),
    path('cache/info/',
         map_cache_info, name="map-cache-info"),
    path('things/',
         map_rectangle_things, name="map-get-things"),
    path('map/', caches_map, name="caches-map"),
    path('show/types/',
         map_show_types, name="map-show-types"),
    path('search/waypoint/',
         map_search_waypoint, name="map-search-by-waypoint")
]
