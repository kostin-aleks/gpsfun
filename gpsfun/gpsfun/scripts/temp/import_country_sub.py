#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.db import connection
#import unittest
#import djyptestutils as yplib
from time import time
from datetime import datetime
import re
from geocaching_su_crawler.Geoname.models import GeoCountry, GeoCountryAdminSubject

#def nonempty_cell(cell):
    #r = Truecontinent
    #if not cell or cell=='&nbsp;':
        #r = False
    #return r


#def date_or_none(cell):
    #r = None
    #if nonempty_cell(cell):
        #parts = cell.split('-')
        #if len(parts) > 2:
            #try:
                #r = datetime(int(parts[0][:4]), int(parts[1]), int(parts[2]))
            #except ValueError:
                #r = None
    #return r

def main():
    start = time() 
    
    GeoCountryAdminSubject.objects.all().delete()
    
    file = open("../../geonames/admin1CodesASCII.txt")

    COLUMN_COUNT = 4
    
    for line in file:
        if not line.startswith('#'):
            print line
            line = line.strip()
            items = line.split("\t")
            cnt = len(items)
            print items[0]
            print items[1]
            print items[2]
            print items[3]
            iso, code = items[0].split('.')
            subject = GeoCountryAdminSubject(country_iso=iso, code = code, name = items[2], geoname_id=int(items[3] or 0))
            subject.save()

    
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
