#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.db import connection
#import unittest
#import djyptestutils as yplib
from time import time
from datetime import datetime
import re
#from BeautifulSoup import BeautifulSoup
from geocaching_su_crawler.Geoname.models import GeoName

def nonempty_cell(cell):
    r = True
    if not cell or cell=='&nbsp;':
        r = False
    return r


def date_or_none(cell):
    r = None
    if nonempty_cell(cell):
        parts = cell.split('-')
        if len(parts) > 2:
            try:
                r = datetime(int(parts[0][:4]), int(parts[1]), int(parts[2]))
            except ValueError:
                r = None
    return r

def main():
    start = time() 
    
    #GeoName.objects.all().delete()
    
    file = open("../../geonames/allCountries.txt")

    for line in file:
        print line
        items = line.split("\t")
        print items[0], items[4], items[5], items[8], items[10], items[-1]
        codes = items[10].split(',')
        try:
            admin_code = int(codes[0])
        except ValueError:
            admin_code = None
        geo_name = GeoName(geo_id=int(items[0]),
                           name = items[2][:127],
                           modification_date=date_or_none(items[-1]),
                           latitude=float(items[4]),
                           longitude=float(items[5]),
                           country_code=items[8],
                           admin1_code=admin_code
                           )
        geo_name.lat_int = int(round(geo_name.latitude*10000))
        geo_name.lng_int = int(round(geo_name.longitude*10000))
        if geo_name.geo_id > 6988317:
            geo_name.save()
        
        #break
    
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
