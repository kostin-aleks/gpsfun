#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.db import connection
#import unittest
#import djyptestutils as yplib
from time import time
from datetime import datetime, date
import json
#import re
#from BeautifulSoup import BeautifulSoup
from gpsfun.main.GeoKrety.models import GeoKret
from gpsfun.main.db_utils import sql2val
from lxml import etree as ET
import urllib2

def main(processed_pid):
    LOAD_GEO_LOCATION = True
    LOAD_GOOGLE_LOCATION = True

    start = time()

    sxml = None

    if LOAD_GEO_LOCATION:
        #.filter(pid=5408)
        #for cach in Cach.objects.all().filter(pid__gt=processed_pid).order_by('pid')[:1990]:
        for geokret in GeoKret.objects.all().filter(country_code__isnull=True, location__isnull=False, state__in=[0, 3]).order_by('gkid')[:200]:
            lat = geokret.latitude_degree
            lng = geokret.longitude_degree

            if lat is not None and lng is not None:
                cnt = 1
                r = 10
                country_code = None
                while cnt < 2:
                    url = 'http://api.geonames.org/countrySubdivision?username=galdor&lat=%s&lng=%s&lang=en&radius=%d' % (lat, lng, r*cnt)
                    f = urllib2.urlopen(url)
                    xml = f.read()
                    try:
                        sxml = ET.XML(xml)
                    except Exception as e:
                        print type(e)
                        print e

                    sub = sxml.getchildren()[0]
                    if sub.tag == 'countrySubdivision':
                        if sub is not None:
                            for node in sub.getchildren():
                                if node.tag == 'countryCode':
                                    txt = node.text
                                    if txt:
                                        country_code = txt.encode('utf8')
                    if country_code:
                        break
                    cnt += 1

                if country_code:
                    geokret.country_code = country_code
                    geokret.save()
            else:
                print geokret.gkid, lat, lng, geokret.location.NS, geokret.location.NS_degree, geokret.location.NS_minute, geokret.location.EW, geokret.location.EW_degree, geokret.loc_EW_minute

    if LOAD_GOOGLE_LOCATION:
        for geokret in GeoKret.objects.all().filter(country_code__isnull=True, location__isnull=False, state__in=[0, 3]).order_by('gkid')[:200]:
            lat = geokret.latitude_degree
            lng = geokret.longitude_degree
            if lat is not None and lng is not None:
                admin_code = None
                country_code = None
                country_name = None
                url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false' % (lat, lng)
                f = urllib2.urlopen(url)
                data = None
                json_str = f.read()
                try:
                    data = json.loads(json_str)
                    if 'status' in data:
                        if data['status'] == 'OK':
                            if 'results' in data:
                                for r in data['results']:
                                    for address in r.get('address_components'):
                                        if 'country' in address.get('types'):
                                            _country_code = address.get('short_name')
                                            if len(_country_code) == 2:
                                                country_code = _country_code
                                                break
                            else:
                                print 'no results', url
                        else:
                            print geokret.id, lat, lng, 'status', data['status']
                    else:
                        print json_str
                except Exception as e:
                    print type(e)
                    print e

                if country_code:
                    geokret.admin_code = admin_code
                    geokret.country_code = country_code
                    geokret.save()
                    print lat, lng, country_code, country_name, admin_code
                else:
                    print  lat, lng, country_code, country_name, admin_code
            else:
                print geokret.gkid, lat, lng, geokret.location.NS, geokret.location.NS_degree, geokret.location.NS_minute, geokret.location.EW, geokret.location.EW_degree, geokret.loc_EW_minute


    sql = """
    SELECT COUNT(*)
    FROM geokret
    WHERE country_code IS NULL AND
    location_id IS NOT NULL AND
    state IN (0, 3)
    """
    undef_country_count = sql2val(sql)
    print "Count of geokrets with undefined country is %s" % undef_country_count

    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    import sys
    processed_pid = 0
    if len(sys.argv) > 1:
        processed_pid = sys.argv[1]

    main(processed_pid)
