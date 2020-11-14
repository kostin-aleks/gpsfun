#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.db import connection
#import unittest
#import djyptestutils as yplib
from time import time
from datetime import datetime, date
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
                admin_code = None
                country_code = None
                while cnt < 2:
                    url = 'http://api.geonames.org/countrySubdivision?username=galdor&lat=%s&lng=%s&lang=en&radius=%d' % (lat, lng, r*cnt)
                    #print
                    #print geokret.gkid, url
                    f = urllib2.urlopen(url)
                    xml = f.read()

                    try:
                        sxml = ET.XML(xml)
                    except Exception as e:
                        print type(e)
                        print e
                        
                    sub = sxml.getchildren()[0]
                    if sub.tag == 'countrySubdivision':
                        #print sub.tag
                        #print xml
                        if sub:
                            for node in sub.getchildren():
                                if node.tag == 'adminCode1':
                                    txt = node.text
                                    if txt:
                                        admin_code = txt.encode('utf8')
                                if node.tag == 'countryCode':
                                    txt = node.text
                                    if txt:
                                        country_code = txt.encode('utf8')    
                    if admin_code and country_code:
                        break
                    cnt += 1                   
                if admin_code and country_code:
                    geokret.admin_code = admin_code
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
                url = 'http://maps.google.com/maps/geo?q=%s,%s&output=xml&sensor=false' % (lat, lng)
                f = urllib2.urlopen(url)
                xml = f.read()
                try:
                    sxml = ET.XML(xml)
                except Exception as e:
                    print type(e)
                    print e
                    
                sub = sxml.getchildren()[0]
                
                if sub.tag == '{http://earth.google.com/kml/2.0}Response':
                    if sub:
                        for node in sub.getchildren():
                            if node.tag == '{http://earth.google.com/kml/2.0}Placemark':
                                for anode in node.getchildren():
                                    if anode.tag == '{urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails':
                                        for a_node in anode.getchildren():
                                            if a_node.tag == '{urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Country':
                                                for thenode in a_node.getchildren():
                                                    if thenode.tag == '{urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}CountryNameCode':
                                                        txt = thenode.text
                                                        if txt:
                                                            country_code = txt.encode('utf8') 
                                                    if thenode.tag == '{urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}CountryName':
                                                        txt = thenode.text
                                                        if txt:
                                                            country_name = txt.encode('utf8')
                                                        if thenode.tag == '{urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeArea':
                                                            txt = thenode.text
                                                            if txt:
                                                                admin_code = txt.encode('utf8')                                                    

              
                if country_code:
                    #geokret.admin_code = admin_code
                    geokret.country_code = country_code
                    geokret.save()
                    #print lat, lng, country_code, country_name, admin_code
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
