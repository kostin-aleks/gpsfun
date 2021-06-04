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
from gpsfun.main.GeoName.models import geocountry_by_code
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_country, get_subdiv_data, get_country_data)


class Command(BaseCommand):
    help = 'Set caches location for all caches'

    def handle(self, *args, **options):
        with requests.Session() as session:
            post = session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )
            r = session.get('https://geocaching.su')
            if not logged(r.text):
                print('Authorization failed')
            else:
                #for cache in Cach.objects.filter(
                        #country_code__isnull=True,
                        #admin_code__isnull=True).order_by('pid'):
                    #country = get_subdiv_data(cache.latitude, cache.longitude)
                    ## print(cache.pid, cache.latitude, cache.longitude)
                    #print(country)
                    #if country and country.get('status') == 'ok':
                        #cache.country_code = country['country_id']
                        #cache.country_name = country['country_name']
                        #cache.admin_code = country['sub_id']
                        #cache.oblast_name = country['sub_name']
                        #cache.save()
                    #elif country.get('status') == 'limit':
                        #break
                #for cache in Cach.objects.filter(
                    #country_code__isnull=True
                #).order_by('pid'):
                    #data = get_country_data(cache.latitude, cache.longitude)
                    #print(data)
                    #if data and data.get('status') == 'ok':
                        #cache.country_code = data['country_iso']
                        #cache.country_name = geocountry_by_code(
                            #data['country_iso']).name
                        #cache.save()

                for cache in Cach.objects.filter(
                    country_code__isnull=True
                    ).order_by('pid'):
                    r = session.get(
                        'http://www.geocaching.su/',
                        params={'pn': 101, 'cid': cache.pid}
                    )
                    country = get_country(r.text)
                    print(country)
                    if country:
                        cache.country = country['country']
                        cache.oblast = country['region']
                        cache.save()


                for cache in Cach.objects.filter(
                    admin_code__isnull=True
                    ).order_by('pid'):
                    r = session.get(
                        'http://www.geocaching.su/',
                        params={'pn': 101, 'cid': cache.pid}
                    )
                    country = get_country(r.text)
                    print(country)
                    if country:
                        cache.country = country['country']
                        cache.oblast = country['region']
                        cache.save()

        log(UPDATE_TYPE.set_caches_locations, 'OK')

        return 'Location of caches has updated'
