"""
urls for application geoname
"""

from django.urls import path
from gpsfun.geoname.views import (
    get_country_regions, get_region_cities, get_waypoint_address)


urlpatterns = [
    path('change/country/', get_country_regions, name="get-country-regions"),
    path('change/region/', get_region_cities, name="get-region-cities"),
    path('address/', get_waypoint_address, name="get-waypoint-address"),
]
