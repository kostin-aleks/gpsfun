#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
import unittest
import djyptestutils as yplib
from time import time
from datetime import datetime, date
import re
import urllib2
import json
from lxml import etree as ET
from BeautifulSoup import BeautifulSoup
from gpsfun.main.GeoMap.models import Geothing
from gpsfun.main.GeoName.models import GeoCountryAdminSubject
from gpsfun.main.models import log 
from gpsfun.main.db_utils import execute_query
from gpsfun.main.db_utils import sql2val

def get_admin_code_by_name(country_code, subject_name):
    subjects = GeoCountryAdminSubject.objects.filter(country_iso=country_code, name=subject_name)
    if subjects.count() == 1:
        return subjects[0].code
    return '777'
 
def main(processed_pid):
    LOAD_GEO_LOCATION = True
    LOAD_GOOGLE_LOCATION = True
    
    start = time() 
   
    if LOAD_GEO_LOCATION:
        for thing in Geothing.objects.all().extra(where=["country_code IS NULL OR admin_code IS NULL OR admin_code='777'"]).order_by('pid')[:100]:
            lat = thing.latitude_degree
            lng = thing.longitude_degree

            if lat is not None and lng is not None:
                cnt = 1
                r = 10
                admin_code = None
                while cnt < 2:
                    url = 'http://api.geonames.org/countrySubdivision?username=galdor&lat=%s&lng=%s&lang=en&radius=%d' % (lat, lng, r*cnt)
                    yplib.get(url)
                    try:
                        soup=yplib.soup()
                    except:
                        pass
                    if soup:
                        item = soup.find('countrysubdivision')
                        if item:
                            if soup.admincode1:
                                admin_code = soup.admincode1.text

                    if admin_code:
                        break
                    cnt += 1

                item = soup.find('countrycode')
                if item and item.text:
                    thing.country_code = item.text.encode('utf8')

                if soup.admincode1:
                    thing.admin_code = soup.admincode1.text

                item = soup.find('countryname')
                if item:
                    thing.country_name = item.text
                if soup.adminname1:
                    thing.oblast_name = soup.adminname1.text

                if thing.country_code and len(thing.country_code)==2:
                    thing.save()
            else:
                print 'no location', thing.pid, lat, lng, thing.location.NS, thing.location.NS_degree, thing.location.NS_minute, thing.location.EW, thing.location.EW_degree, thing.loc_EW_minute

    if LOAD_GOOGLE_LOCATION:
        for thing in Geothing.objects.all().extra(where=["country_code IS NULL OR country_name IS NULL OR admin_code IS NULL OR admin_code='777'"]).order_by('pid')[:100]:
            lat = thing.latitude_degree
            lng = thing.longitude_degree
            if lat is not None and lng is not None:
                admin_name = None
                country_code = None
                country_name = None
                admin_code = None
                url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false' % (lat, lng)
                f = urllib2.urlopen(url)
                data = f.read()
                try:
                    r = json.loads(data)
                except Exception as e:
                    print type(e)
                    print e
                if r.get('status') == 'OK' and len(r.get('results')):
                    for result in r.get('results'):
                        if len(result.get('address_components')):
                            for address in  result.get('address_components'):
                                types = address.get("types")
                                if "country" in types and "political" in types:
                                    country_code = address.get("short_name")
                                if "administrative_area_level_1" in types and "political" in types:
                                    admin_name = address.get("short_name")
                                    if len(admin_name) < 6:
                                        admin_name = address.get("long_name")

                if country_code:
                    thing.country_code = country_code
                    thing.oblast = admin_name
                    thing.admin_code = get_admin_code_by_name(country_code, admin_name)
                    thing.save()
                else:
                    print  lat, lng, country_code, country_name, admin_name
            else:
                print thing.pid, lat, lng, thing.location.NS, thing.location.NS_degree, thing.location.NS_minute, thing.location.EW, thing.location.EW_degree, thing.loc_EW_minute

    sql = """
    UPDATE geothing gt
    LEFT JOIN oblast_subject os ON (
        gt.country_code=os.country_iso and gt.oblast=os.oblast
        )
    SET gt.admin_code=os.code
    WHERE os.id IS NOT NULL
    """
    r = execute_query(sql)
    
    sql = """
    UPDATE geothing 
    SET admin_code='777', 
    oblast_name='undefined subject' 
    WHERE country_code IS NOT NULL AND admin_code IS NULL
    """
    r = execute_query(sql)
    
    sql = """
    update geothing gt 
    left join geo_country c on gt.country_code=c.iso 
    set gt.country_name=c.name
    """
    r = execute_query(sql)
    
    sql = """
    update geothing gt 
    left join geo_country_subject c on gt.admin_code=c.code and gt.country_code=c.country_iso 
    set gt.oblast_name=c.name
    where gt.admin_code='777'
     """
    r = execute_query(sql)
    
    sql = """
    update geothing
    set country_code='RU',
    admin_code='82',
    country = 'Россия',
    oblast = 'Республика Крым',
    country_name = 'Russia',
    oblast_name = 'Respublika Krym'
    where country_code='UA' and admin_code='11'
     """
    r = execute_query(sql)

    sql = """SELECT COUNT(*) FROM geothing WHERE country_code IS NULL"""
    undefined_country_count = sql2val(sql)
    sql = """SELECT COUNT(*) FROM geothing WHERE admin_code IS NULL OR admin_code = '777'"""
    undefined_subject_count = sql2val(sql)
    undefined_count = '%s/%s' % (undefined_country_count, undefined_subject_count)
    
    log('map_set_location', 'OK %s'%undefined_count)
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    import sys
    processed_pid = 0
    if len(sys.argv) > 1:
        processed_pid = sys.argv[1]

    main(processed_pid)
