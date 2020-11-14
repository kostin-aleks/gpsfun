#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime, date
import re
from BeautifulSoup import BeautifulSoup
from gpsfun.main.GeoCachSU.models import Geocacher, Cach

def point_in_rectangle(p, r):
    if p['lat'] > r['LT']['lat']:
        return False
    if p['lat'] < r['RB']['lat']:
        return False
    if p['lon'] < r['LT']['lon']:
        return False
    if p['lon'] > r['RB']['lon']:
        return False
    return True

def main():
    
    start = time() 
    caches = Cach.objects.filter(country_code='RU', admin_code='47').filter(cach_type__icontains='городской')
    print caches.count()
    Moscow_rectangle = {'LT': {'lat': 55.91667, 'lon': 37.35},
                        'RB': {'lat': 55.55, 'lon': 37.85},
    }
    for cache in caches:
        #if point_in_rectangle({'lat': cache.latitude_degree, 'lon': cache.longitude_degree}, Moscow_rectangle):
        if True:
            cache.admin_code = '48'
            cache.save()
            print cache.code, cache.cach_type.encode('utf-8'), cache.latitude_degree, cache.longitude_degree
        
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
