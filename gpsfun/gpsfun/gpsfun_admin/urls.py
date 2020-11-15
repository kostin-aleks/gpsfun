# from django.conf.urls import *
from django.urls import path
from gpsfun.gpsfun_admin.views import (
    index, last_updates, data_updating_log, check_data)


urlpatterns = [
    path('', index, name="gpsfun-admin-index"),
    path('last_updates/', last_updates,
        name="gpsfun-admin-last-updates"),
    path('data_updating_log/', data_updating_log,
        name="gpsfun-admin-updating-log"),
    path('check/data/', check_data,
        name="gpsfun-admin-check-data"),
]
