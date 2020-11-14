#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoKrety.models import GeoKret, Location
from gpsfun.main.db_utils import execute_query
from lxml import etree as ET
import sys
import os


def main():
    LOAD_CACHES = True
    
    start = time() 
    
    GeoKret.objects.all().delete()
    
    file = '/tmp/export2-full.xml'   
     
    # sanity checking, only work on wpt files
    if file.endswith('.xml') == 0: sys.exit(-1)
     
    print "Reading file: "+file
    
    fh = open(file,'r')
    xml = fh.read()
    fh.close()

    sxml = ET.XML(xml)

    
    all_krety = sxml.getchildren()[0]
    for kret in all_krety:
        geokret = GeoKret()
        geokret.gkid = int(kret.get('id') or 0)
        geokret.name = kret.text
        geokret.distance =  int(kret.get('dist') or 0)
        location = Location()
        if kret.get('lat') and kret.get('lon'):
            location.NS_degree = float(kret.get('lat'))
            location.EW_degree = float(kret.get('lon'))
            location.save()
        else:
            location = None
        geokret.location = location
        geokret.waypoint = kret.get('waypoint')
        geokret.owner_id = int(kret.get('owner_id')) if kret.get('owner_id') else None
        geokret.state = int(kret.get('state')) if kret.get('state') else None
        type_ = kret.get('type') if len(kret.get('type')) else '0'
        geokret.type_code = int(type_)
        geokret.image = kret.get('image')
        geokret.save()
        
        #print kret.get('id'), kret.text, kret.get('dist'), kret.get('lat'), kret.get('lon'), kret.get('waypoint'), kret.get('owner_id'), kret.get('state'), kret.get('type'), kret.get('image')  
    # set country and admin subject
    sql = """
    UPDATE geokret gk 
    LEFT JOIN geothing t ON gk.waypoint = t.code
    SET gk.country_code = t.country_code, gk.admin_code = t.admin_code
    WHERE gk.waypoint IS NOT NULL AND gk.waypoint != '' AND t.id IS NOT NULL
    """
    r = execute_query(sql)
    
    
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
