#!/usr/bin/env python
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
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_country)


class Command(BaseCommand):
    """ Command """
    help = 'Set caches location for all caches'

    def handle(self, *args, **options):
        with requests.Session() as session:
            session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )
            response = session.get('https://geocaching.su')
            if not logged(response.text):
                print('Authorization failed')
            else:
                for cache in Cach.objects.filter(
                    country_code__isnull=True
                ).order_by('pid'):
                    response = session.get(
                        'http://www.geocaching.su/',
                        params={'pn': 101, 'cid': cache.pid}
                    )
                    country = get_country(response.text)
                    print(country)
                    if country:
                        cache.country = country['country']
                        cache.oblast = country['region']
                        cache.save()


                for cache in Cach.objects.filter(
                    admin_code__isnull=True
                    ).order_by('pid'):
                    response = session.get(
                        'http://www.geocaching.su/',
                        params={'pn': 101, 'cid': cache.pid}
                    )
                    country = get_country(response.text)
                    print(country)
                    if country:
                        cache.country = country['country']
                        cache.oblast = country['region']
                        cache.save()

        log(UPDATE_TYPE.set_caches_locations, 'OK')

        return 'Location of caches has updated'
