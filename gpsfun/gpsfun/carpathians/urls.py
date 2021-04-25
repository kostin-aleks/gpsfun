from django.urls import path
from gpsfun.carpathians.views import (routes, )


urlpatterns = [
    path('', routes, name="routes-list"),
]
