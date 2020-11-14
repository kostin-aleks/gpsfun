#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     set_cache_location.py

DESCRIPTION
     Set location (country, subject) for all caches
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.GeoCachSU.models import Cach
from gpsfun.geocaching_su_stat.utils import get_country_data


class Command(BaseCommand):
    help = 'Set caches location for all caches'

    def handle(self, *args, **options):
        with requests.Session() as session:
            for cache in Cach.objects.filter(
                    country_code__isnull=True,
                    admin_code__isnull=True).order_by('pid'):
                country = get_country_data(cache.latitude, cache.longitude)
                print(country)
                if country and country.get('status') == 'ok':
                    cache.country_code = country['country_id']
                    cache.country_name = country['country_name']
                    cache.admin_code = country['sub_id']
                    cache.oblast_name = country['sub_name']
                    cache.save()
                elif country.get('status') == 'limit':
                    break

        log(UPDATE_TYPE.set_caches_locations, 'OK')

        return 'Location of caches has updated'
