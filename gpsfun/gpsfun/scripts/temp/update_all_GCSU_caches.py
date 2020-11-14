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
from BeautifulSoup import BeautifulStoneSoup
from gpsfun.main.db_utils import execute_query
from DjHDGutils.dbutils import get_object_or_none

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

def update_geothing(geothing, the_geothing, the_location):
    def int_minutes(m):       
        return int(round(m*1000))
    
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
   
    file = '/tmp/geocaching_su.wpt'   
     
    # sanity checking, only work on wpt files
    if file.endswith('.wpt') == 0: sys.exit(-1)
     
    print "Reading file: "+file
     
    fh = codecs.open(file,'r',"cp1251")
    wpt = fh.readlines()
    fh.close()
     
    WPT_CODE = 1
    WPT_LAT = 2
    WPT_LON = 3
    WPT_TITLE = 10
    WPT_DATE = 4
    
    geosite = Geosite.objects.get(code='GC_SU')
    print geosite
    print len(wpt), 'points'
    k = 0
    for point in wpt:
        k += 1
        fields = point.split(',')
        if fields[0].isdigit():
            the_geothing = TheGeothing()
            the_location = TheLocation()

            lat_degree = float(fields[WPT_LAT])
            the_location.NS_degree = lat_degree
            #the_location.NS_minute = (abs(lat_degree) - abs(the_location.NS_degree)) * 60
            lon_degree = float(fields[WPT_LON])
            the_location.EW_degree = lon_degree            
            #the_location.EW_minute = (abs(lon_degree) - abs(the_location.EW_degree)) * 60

            p = re.compile('(\D+)(\d+)') 
            dgs = p.findall(fields[WPT_CODE])
            if dgs:
                code_data = dgs[0]
                the_geothing.code = fields[WPT_CODE]
                the_geothing.pid = int(code_data[1])
                the_geothing.type_code = code_data[0]

            p = re.compile(u'(.+)от(.+)') 
            dgs = p.findall(fields[WPT_TITLE])
            if dgs:
                title = dgs[0]
                the_geothing.name = title[0]
                the_geothing.author = title[1]

            d = float(fields[WPT_DATE])

            the_geothing.created_date = Dephi_date_to_python_date(d)
            
            if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)
                if geothing is not None:
                    update_geothing(geothing, the_geothing, the_location)
                else:
                    create_new_geothing(the_geothing, the_location, geosite)

    
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
