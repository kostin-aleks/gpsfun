#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.main.models import log
from gpsfun.main.GeoName.models import GeoCountry
import urllib2
import json
from DjHDGutils.dbutils import get_object_or_none
#from  gpsfun.main.utils import update_geothing, \
      #create_new_geothing, TheGeothing, TheLocation

MY_KEY = 'D47WtT9HJydnSS3t'
RECTANGLES = [
    (-90, 0, 0, 180),
    (-90, -180, 0, 0),
    (0, -180, 60, -120),
    (60, -180, 90, -120),
    (0, -120, 30, -60),
        (30, -120, 45, -90),
            (30, -90, 38, -60),
            (38, -90, 45, -75),
            (38, -75, 45, -60),
        (45, -120, 60, -90),
        (45, -90, 60, -60),
    (60, -120, 90, -60),
    (0, -60, 30, 0),
    (30, -60, 60, 0),
    (60, -60, 90, 0),
    (0, 0, 30, 60),
        (30, 0, 45, 60),
            (45, 0, 52, 15),
            (52, 0, 60, 15),
            (45, 15, 52, 30),
            (52, 15, 60, 30),
        (45, 30, 60, 60),
    (60, 0, 90, 60),
    (0, 60, 30, 120),
    (30, 60, 90, 120),
    (0, 120, 30, 180),
    (30, 120, 90, 180),
]

url_pattern = 'http://www.opencaching.com/api/geocache/?Authorization=%s&bbox=%s&limit=5000'


Z0 = {'1': 29, '0': 30, '3': 27, '2': 28, '5': 25, '4': 26, '7': 23, '6': 24, '9': 21, '8': 22, 'A': 20,
      'C': 18, 'B': 19, 'E': 16, 'D': 17, 'G': 14, 'F': 15, 'H': 13, 'K': 11, 'J': 12, 'M': 10, 'N': 9,
      'Q': 7, 'P': 8, 'R': 6, 'T': 5, 'W': 3, 'V': 4, 'Y': 1, 'X': 2, 'Z': 0, 'U': 31}

Power32 = {0: 1, 1: 32, 2: 1024, 3: 32768, 4: 1048576}

TYPE_TO_CODE = {'Traditional Cache': 'TR',
                'Multi-cache': 'TS',
                'Unknown Cache': 'OT',
                'Virtual Cache': 'VI',
                }

def dig32(s):
    p = re.compile('[ZYXWVTRQPNMKJHGFEDCBA9876543210]{1,5}')
    if not p.match(s):
        return None
    l = len(s)
    r = 0
    for i in range(l):
        ch = s[i]
        v = Z0[ch]
        r += v*Power32.get((l-1)-i)
    return r

def get_occom_date(hidden):
    if hidden is None:
        return None
    days = int(round(float(hidden)/1000.0/86400, 0))

    return date(1970, 1, 1) + timedelta(days=days)

def type_code_occom(type_description):
    return TYPE_TO_CODE.get(type_description, '')

def iso_by_country_name(country_name):
    r = None
    country = get_object_or_none(GeoCountry, name=country_name)
    if country:
        r = country.iso
    return r

class TheLocation:
    NS_degree = None
    EW_degree = None
    NS_minute = None
    EW_minute = None

def create_new_geothing(the_geothing, the_location, geosite):
    #print geosite.id
    geothing = Geothing(geosite=geosite)
    l = Location()
    l.NS_degree = the_location.NS_degree
    l.EW_degree = the_location.EW_degree
    l.NS_minute = the_location.NS_minute
    l.EW_minute = the_location.EW_minute
    l.save()
    geothing.location = l
    geothing.pid = the_geothing.get('pid')
    geothing.code = the_geothing.get('oxcode')
    geothing.type_code = the_geothing.get('type_code')
    geothing.name = the_geothing.get('name')
    geothing.created_date = the_geothing.get('created_date')
    geothing.author = the_geothing.get('author')
    geothing.country_name = the_geothing.get('country_name')
    geothing.country_code = the_geothing.get('country_code')
    print 'NEW', geothing.code
    geothing.save()

def update_geothing(geothing, the_geothing, the_location):
    def int_minutes(m):
        return int(round(m*1000))

    changed = False
    if geothing.code != the_geothing.get('oxcode'):
        changed = True
        geothing.code = the_geothing.get('oxcode')
    if geothing.type_code != the_geothing.get('type_code'):
        changed = True
        geothing.type_code = the_geothing.get('type_code')
    if geothing.name != the_geothing.get('name'):
        changed = True
        geothing.name = the_geothing.get('name')
    if geothing.author != the_geothing.get('author'):
        changed = True
        geothing.author = the_geothing.get('author')
    #if geothing.code != the_geothing.get('code'):
        #changed = True
        #geothing.code = the_geothing.get('code')

    location_changed = False
    if int(geothing.location.NS_degree*1000000) != int(the_location.NS_degree*1000000):
        location_changed = True
        geothing.location.NS_degree = the_location.NS_degree
    if int(geothing.location.EW_degree*1000000) != int(the_location.EW_degree*1000000):
        location_changed = True
        geothing.location.EW_degree = the_location.EW_degree

    if location_changed:
        geothing.location.save()
        geothing.country_code = None
        geothing.admin_code = None
        geothing.country_name = None
        geothing.oblast_name = None

    if changed or location_changed:
        print 'SAVED', geothing.code
        geothing.save()
        return 1


def process(rectangle, geosite, uc, nc):
    print 'process'
    print rectangle
    print geosite
    print uc, nc
    bbox = [str(x) for x in  rectangle]
    #print bbox
    url = url_pattern % (MY_KEY, ','.join(bbox))
    print url
    response = urllib2.urlopen(url)
    data = response.read()
    #print data
    caches = json.loads(data)
    for cache in caches:
        name = cache.get('name','')
        if name:
            name = name.replace('\n','').strip()
        cache['name'] = name
        the_location = TheLocation()
        l = cache.get('location')
        if l:
            lat_degree = l.get('lat')
            lon_degree = l.get('lon')
            the_location.NS_degree = lat_degree
            the_location.EW_degree = lon_degree

        p = re.compile('OX([\dA-Z]+)')
        code = cache.get('oxcode').upper()
        dgs = p.findall(code)
        if dgs:
            code_data = dgs[0]
            cache['pid'] = dig32(code_data)
            cache['type_code'] = type_code_occom(cache.get('type'))

        cache['created_date']  = get_occom_date(cache.get('hidden'))
        a = cache.get('hidden_by')
        if a:
            cache['author'] = a.get('name')
        region = cache.get('region')
        if region:
            cache['country_name'] = region.get('country')
            cache['country_code'] = iso_by_country_name(cache['country_name'])
        if not code or not cache.get('pid'):
            print 'ERROR: NO CODE'
            print cache
            continue

        geothing = get_object_or_none(Geothing, pid=cache.get('pid'), geosite=geosite)
        if geothing is not None:
            uc += update_geothing(geothing, cache, the_location) or 0
        else:
            create_new_geothing(cache, the_location, geosite)
            nc += 1
    return uc, nc

def main():
    LOAD_CACHES = True

    start = time()
    uc = 0
    nc = 0

    geosite = Geosite.objects.get(code='OC_COM')
    for rec in RECTANGLES:
        uc, nc = process(rec, geosite, uc, nc)

    message = 'OK. updated %s, new %s' % (uc, nc)
    log('map_occom_caches', message)
    print message
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
