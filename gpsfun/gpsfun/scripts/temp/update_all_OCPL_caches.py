#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime, date, timedelta
import re
from BeautifulSoup import BeautifulSoup
#from gpsfun.main.GeoCachSU.models import GEOCACHING_SU_ONMAP_TYPES
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from lxml import etree as ET
import sys
import os
import codecs
import csv
import urllib2
import json
from BeautifulSoup import BeautifulStoneSoup
from gpsfun.main.db_utils import execute_query
from DjHDGutils.dbutils import get_object_or_none

OCPL_TYPES = {
    'Virtual': 'VI',
    'Traditional': 'TR',
    'Multi': 'MS',
    'Quiz': 'QZ',
    'Other': 'OT',
    'Moving': 'MO',
    'Event': 'EV',
    'Webcam': 'WC',    
    }

class TheGeothing:
    pid = None
    code = None
    name = None
    created_date = None
    author = None
    type_code = None

class TheLocation:
    NS_degree = None
    EW_degree = None
    NS_minute = None
    EW_minute = None

def create_new_geothing(the_geothing, the_location, geosite):
    geothing = Geothing(geosite=geosite)
    l = Location()
    l.NS_degree = the_location.NS_degree
    l.EW_degree = the_location.EW_degree
    l.NS_minute = the_location.NS_minute
    l.EW_minute = the_location.EW_minute
    l.save()
    geothing.location = l
    geothing.pid = the_geothing.pid
    geothing.code = the_geothing.code
    geothing.type_code = the_geothing.type_code
    geothing.name = the_geothing.name
    geothing.created_date = the_geothing.created_date
    geothing.author = the_geothing.author
    print 'NEW', geothing.pid
    geothing.save()

def int_minutes(m):       
        return int(round(m*1000))
    
def location_was_changed(location, the_location):
    location_changed = False
    if int(location.NS_degree*1000000) != int(the_location.NS_degree*1000000):
        location_changed = True
    if int(location.EW_degree*1000000) != int(the_location.EW_degree*1000000):
        location_changed = True
    #if int_minutes(location.NS_minute) != int_minutes(the_location.NS_minute):
        #location_changed = True
    #if int_minutes(location.EW_minute) != int_minutes(the_location.EW_minute):
        #location_changed = True
    return location_changed
    
    
def update_geothing(geothing, the_geothing, the_location):    
    changed = False
    if geothing.code != the_geothing.code:
        changed = True
        geothing.code = the_geothing.code
    if geothing.type_code != the_geothing.type_code:
        changed = True
        geothing.type_code = the_geothing.type_code
    if geothing.name != the_geothing.name:
        changed = True
        geothing.name = the_geothing.name
    if geothing.author != the_geothing.author:
        changed = True
        geothing.author = the_geothing.author        
    if geothing.code != the_geothing.code:
        changed = True
        geothing.code = the_geothing.code
        
    location_changed = False
    if int(geothing.location.NS_degree*1000000) != int(the_location.NS_degree*1000000):
        location_changed = True
        geothing.location.NS_degree = the_location.NS_degree
    if int(geothing.location.EW_degree*1000000) != int(the_location.EW_degree*1000000):
        location_changed = True
        geothing.location.EW_degree = the_location.EW_degree
    #if int_minutes(geothing.location.NS_minute) != int_minutes(the_location.NS_minute):
        #location_changed = True
        #geothing.location.NS_minute = the_location.NS_minute
    #if int_minutes(geothing.location.EW_minute) != int_minutes(the_location.EW_minute):
        #location_changed = True
        #geothing.location.EW_minute = the_location.EW_minute
    
    if location_changed:
        geothing.location.save()
        geothing.country_code = None
        geothing.admin_code = None
        geothing.country_name = None
        geothing.oblast_name = None

    if changed or location_changed:
        print 'SAVED', geothing.pid
        geothing.save()
    
        
def Dephi_date_to_python_date(d):
    days = int(d)
    hours = int(round((d - days)*24))
    date_ = datetime(1899, 12, 30) + timedelta(days=int(d), hours=hours)
    return date_

def main():
    LOAD_CACHES = True
    
    start = time() 
   
    file = '/tmp/ocpl.wpt'   
     
    # sanity checking, only work on wpt files
    if file.endswith('.wpt') == 0: sys.exit(-1)
     
    print "Reading file: "+file
     
    fh = codecs.open(file,'r',"utf-8")
    wpt = fh.readlines()
    fh.close()
     
    WPT_CODE = 10
    WPT_LAT = 2
    WPT_LON = 3
    WPT_TITLE = 1
    WPT_DATE = 4
    MY_CONSUMER_KEY = 'fky3LF9xvWz9y7Gs3tZ6'
    FIELDS = 'code|name|location|type|status|url|owner|date_created'
    geocach_api_request = 'http://opencaching.pl/okapi/services/caches/geocache?cache_code=%s&consumer_key=%s&fields=%s'
    
    geosite = Geosite.objects.get(code='OCPL')
    print geosite
    print len(wpt), 'points'
    k = 0
    for point in wpt:
        k += 1
        fields = point.split(',')
        if fields[0]=='-1':
            the_geothing = TheGeothing()
            the_location = TheLocation()

            lat_degree = float(fields[WPT_LAT])
            the_location.NS_degree = lat_degree
            #the_location.NS_minute = (abs(lat_degree) - abs(the_location.NS_degree)) * 60
            lon_degree = float(fields[WPT_LON])
            the_location.EW_degree = lon_degree
            #the_location.EW_minute = (abs(lon_degree) - abs(the_location.EW_degree)) * 60

            code_str = fields[WPT_CODE]
            parts = code_str.split('/')
            if len(parts)==4:
                cache_code = parts[0]
                the_geothing.code = cache_code
                the_geothing.name = fields[WPT_TITLE]
                geothing = get_object_or_none(Geothing, code=the_geothing.code, geosite=geosite)
                if geothing:
                    if the_geothing.name == geothing.name and not location_was_changed(geothing.location, the_location):
                        continue
                print the_geothing.code, 'changed'
                url = geocach_api_request % (cache_code, MY_CONSUMER_KEY, FIELDS)
                try:                    
                    response = urllib2.urlopen(url)
                    json_str = response.read()
                    cache_data = json.loads(json_str)
                    if cache_data.get('status') != 'Available':
                        continue
                    the_geothing.type_code = OCPL_TYPES.get(cache_data.get('type'))
                    cache_url = cache_data.get('url')
                    if not cache_url:
                        continue
                    p = re.compile(u'(\d+)$')
                    dgs = p.findall(cache_url)
                    the_geothing.pid = int(dgs[0])
                    owner_name = ''
                    if cache_data.get('owner'):
                        owner_name = cache_data.get('owner').get('username')
                    the_geothing.author = owner_name
                    
                    date_created = cache_data.get('date_created')
                    if date_created:
                        date_created = date_created[:10]
                        parts = date_created.split('-')
                        if parts and len(parts) == 3:
                            dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                            the_geothing.created_date = dt

                except:
                    print 'exception'
                    continue

            if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)
                if geothing is not None:
                    update_geothing(geothing, the_geothing, the_location)
                else:
                    create_new_geothing(the_geothing, the_location, geosite)
            #break

    
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
