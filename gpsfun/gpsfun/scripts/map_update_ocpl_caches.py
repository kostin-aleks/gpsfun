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
from gpsfun.main.models import log
from gpsfun.main.db_utils import sql2list, sql2val
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
    print('NEW', geothing.pid)
    geothing.save()

def int_minutes(m):
        return int(round(m*1000))

def location_was_changed(location, the_location):
    location_changed = False
    if int(location.NS_degree*1000000) != int(the_location.NS_degree*1000000):
        location_changed = True
    if int(location.EW_degree*1000000) != int(the_location.EW_degree*1000000):
        location_changed = True
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

    if location_changed:
        geothing.location.save()
        geothing.country_code = None
        geothing.admin_code = None
        geothing.country_name = None
        geothing.oblast_name = None

    if changed or location_changed:
        print('SAVED', geothing.pid)
        geothing.save()


def Dephi_date_to_python_date(d):
    days = int(d)
    hours = int(round((d - days)*24))
    date_ = datetime(1899, 12, 30) + timedelta(days=int(d), hours=hours)
    return date_

def main():
    LOAD_CACHES = True

    start = time()

    yplib.set_up()
    yplib.set_debugging(False)

    # log in
    r = yplib.post2('http://opencaching.pl/login.php',
            (('LogMeIn','zaloguj'), ('email', 'kurianin'), ('password','gjhjkjy'), ('action', 'login'), ('target', 'index.php')))

    soup=yplib.soup()

    a = soup.find('a', text='kurianin')
    if not a:
        print('Authorization failed')
        return False
    print('OK')

    # get wpt file
    r = yplib.get('http://opencaching.pl/search.php?searchto=searchbyname&showresult=1&expert=0&output=HTML&sort=bycreated&f_inactive=1&f_ignored=1&f_userfound=1&f_userowner=1&f_watched=0&f_geokret=0&country=PL&region=&cachetype=1111111110&cache_attribs=&cache_attribs_not=&cachesize_1=1&cachesize_2=1&cachesize_3=1&cachesize_4=1&cachesize_5=1&cachesize_6=1&cachesize_7=1&cachevote_1=-3&cachevote_2=3.000&cachenovote=1&cachedifficulty_1=1&cachedifficulty_2=5&cacheterrain_1=1&cacheterrain_2=5&cacherating=0&cachename=%25&cachename=')
    soup = yplib.soup(cp='utf8')
    link_to_wpt = ''

    wpt_link = re.compile('ocpl\d+\.wpt\?.+count\=max.*')
    a_list = soup.findAll('a', {'class':"links", 'title': "Oziexplorer .wpt"})
    if a_list:
        for a in a_list:
            if a.get('href') and wpt_link.match(a.get('href')):
                link_to_wpt = a.get('href')
                break
    print(link_to_wpt)

    if link_to_wpt:
        r = yplib.get(link_to_wpt)
        soup = yplib.soup(cp='utf8')
        wpt = soup.text.split('\n')
    else:
        print('oblom')
        return

    WPT_CODE = 10
    WPT_LAT = 2
    WPT_LON = 3
    WPT_TITLE = 1
    WPT_DATE = 4
    MY_CONSUMER_KEY = 'fky3LF9xvWz9y7Gs3tZ6'
    FIELDS = 'code|name|location|type|status|url|owner|date_created'
    geocach_api_request = 'http://opencaching.pl/okapi/services/caches/geocache?cache_code=%s&consumer_key=%s&fields=%s'

    geosite = Geosite.objects.get(code='OCPL')
    print(geosite)
    print(len(wpt), 'points')
    k = 0
    uc = 0
    nc = 0
    for point in wpt:
        k += 1
        fields = point.split(',')
        if fields[0]=='-1':
            the_geothing = TheGeothing()
            the_geothing.pid=1
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
                geothing_items = Geothing.objects.filter(code=the_geothing.code, geosite=geosite)
                if geothing_items.count() > 0:
                    geothing = geothing_items[0]
                    if the_geothing.name == geothing.name and not location_was_changed(geothing.location, the_location):
                        continue

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
                    p = re.compile(u'OP([\dA-F]+)$')
                    dgs = p.findall(cache_url)
                    the_geothing.pid = int(dgs[0], 16)
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
                    print
                    print('exception.')
                    print(url)
                    print(cache_data)
                    continue

            if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)
                if geothing is not None:
                    update_geothing(geothing, the_geothing, the_location)
                    uc += 1
                else:
                    create_new_geothing(the_geothing, the_location, geosite)
                    nc += 1

    sql = """
    select COUNT(*)
    FROM
    (
    select g.code as code, count(id) as cnt
    from geothing g
    group by g.code
    having cnt > 1
    ) as tbl
    """
    dc = sql2val(sql)
    message = 'OK. updated %s, new %s, doubles %s' % (uc, nc, dc)
    log('map_ocpl_caches', message)
    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
