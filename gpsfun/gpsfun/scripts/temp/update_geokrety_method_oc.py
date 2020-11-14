#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoKrety.models import GeoKret, Location
from gpsfun.main.models import LogUpdate
from lxml import etree as ET
import sys
import os
import urllib2

class TheLocation:
    latitude = None
    longitude = None
    
class TheGeoKret:
    gkid = None
    name = None
    distance = None
    location = None
    waypoint = None
    state = None
    
def main():
    LOAD_CACHES = True
    
    start = time() 
    
    #log = LogUpdate()
    #log.update_type = 'kret'
    #log.update_date = datetime.now()
    #log.message = 'begin'
    #log.save()

    sincedate = datetime.now() - timedelta(days=2)
    sincedatestr = sincedate.strftime('%Y%m%d%H%M%S')
    url = 'http://geokrety.org/export_oc.php?modifiedsince=%s' % sincedatestr
    print url 
    f = urllib2.urlopen(url)
    xml = f.read()
    #log = LogUpdate()
    #log.update_type = 'kret'
    #log.update_date = datetime.now()
    #log.message = 'open %s' % url
    #log.save()

    try:
        sxml = ET.XML(xml)
    except Exception as e:
        print type(e)
        print e
        return

    #log = LogUpdate()
    #log.update_type = 'kret'
    #log.update_date = datetime.now()
    #log.message = 'xml parsed'
    #log.save()
    
    cnt = 0
    all_krety = sxml.getchildren()
    for kret in all_krety:
        gkid = int(kret.get('id') or 0)
        if not gkid:
            continue
        geokret, ok = GeoKret.objects.get_or_create(gkid=gkid)
        changed_kret = False
        for node in kret.getchildren():
            if node.tag == 'name':
                if geokret.name != node.text:
                    geokret.name = node.text
                    changed_kret = True
            if node.tag == 'distancetravelled':
                if geokret.distance !=  int(node.text or 0):
                    geokret.distance =  int(node.text or 0)
                    changed_kret = True
            if node.tag == 'state':
                state =  int(node.text) if node.text else None
                if state != geokret.state:
                    geokret.state = state
                    changed_kret = True
            if node.tag == 'position':
                location = Location()
                if node.get('latitude') and node.get('longitude'):
                    location.NS_degree = float(node.get('latitude'))
                    location.EW_degree = float(node.get('longitude'))                   
                else:
                    location = None
                
                if (location is None and geokret.location is not None) or (location is not None and geokret.location is None):
                    if location:
                        location.save()
                    geokret.location = location
                    geokret.country_code = None
                    changed_kret = True
                else:
                    if location and geokret.location:
                        if location and location.NS_degree != geokret.location.NS_degree or \
                           location.EW_degree != geokret.location.EW_degree:
                            location.save()
                            geokret.location = location
                            geokret.country_code = None
                            changed_kret = True
            if node.tag == 'waypoints':
                wps = node.getchildren()
                if wps and len(wps):
                    wp = wps[0]
                    if wp.text != geokret.waypoint:
                        geokret.waypoint = wp.text
                        changed_kret = True
        if changed_kret:
            geokret.save()
            #print 'saved', geokret.gkid, geokret.name, geokret.distance, geokret.location, geokret.waypoint, geokret.state
            cnt += 1

    log = LogUpdate()
    log.update_type = 'kret'
    log.update_date = datetime.now()
    log.message = 'success, url=%s, updatet/added %s' % (url, cnt)    
    log.save()
    elapsed = time() - start
    #print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
