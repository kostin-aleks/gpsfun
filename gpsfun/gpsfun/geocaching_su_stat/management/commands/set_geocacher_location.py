#!/usr/bin/env python
"""
NAME
     set_geocacher_location.py

DESCRIPTION
     Set location (country, subject) for all caches
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.models import log, UpdateType
from gpsfun.main.GeoCachSU.models import Geocacher
from gpsfun.main.GeoName.models import GeoCountry
from gpsfun.geocaching_su_stat.utils import get_subdiv_data


class Command(BaseCommand):
    """ Command """
    help = 'Set geocachers location for all geocachers'

    def handle(self, *args, **options):
        with requests.Session() as session:
            for geocacher in Geocacher.objects.filter(
                    country_iso3__isnull=True,
                    admin_code__isnull=True):
                country = get_subdiv_data(
                    geocacher.latitude, geocacher.longitude)
                print(country)
                if country and country.get('status') == 'ok':
                    gcountry = get_object_or_none(
                        GeoCountry, iso=country.get('country_id'))
                    if gcountry is not None:
                        geocacher.country_iso3 = gcountry.iso3
                        geocacher.country = gcountry.name
                        geocacher.admin_code = country['sub_id']
                        geocacher.oblast = country['sub_name']
                        geocacher.save()
                elif country.get('status') == 'limit':
                    break

        log(UpdateType.set_geocachers_locations, 'OK')

        return 'Location of geocachers has updated'
