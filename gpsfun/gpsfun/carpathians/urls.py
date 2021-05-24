from django.urls import path
from gpsfun.carpathians.views import (
    ridges, ridge, peak, route, routes, peaks)


urlpatterns = [
    path('ridges/', ridges, name="ridges"),
    path('ridge/<slug>/', ridge, name="ridge"),
    path('peak/<slug>/', peak, name="peak"),
    path('peaks/', peaks, name="peaks"),
    path('route/<int:route_id>/', route, name="route"),
    path('', routes, name="routes"),
]
