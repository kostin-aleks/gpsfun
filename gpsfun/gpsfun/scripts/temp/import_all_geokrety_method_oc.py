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
from DjHDGutils.dbutils import get_object_or_none

def main():
    LOAD_CACHES = True
    
    start = time() 
    
    file = '/tmp/export_oc-full.xml'   
     
    # sanity checking, only work on wpt files
    if file.endswith('.xml') == 0: sys.exit(-1)
    
    #sql = """ UPDATE geokret gk SET gk.state = NULL  """
    #r = execute_query(sql)
    
    print "Reading file: "+file
    
    fh = open(file,'r')
    xml = fh.read()
    fh.close()

    sxml = ET.XML(xml)
   
    all_krety = sxml.getchildren()
    for kret in all_krety:
        
        gkid = int(kret.get('id') or 0)
        if not gkid:
            continue

        geokret = get_object_or_none(GeoKret, gkid=gkid)
        if geokret:
            for node in kret.getchildren():
                if node.tag == 'state':
                    geokret.state = int(node.text) if node.text else None
            geokret.save()    


    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
