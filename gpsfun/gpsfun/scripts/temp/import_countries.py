#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from django.db import connection
#import unittest
#import djyptestutils as yplib
from time import time
from datetime import datetime
import re
#from BeautifulSoup import BeautifulSoup
from geocaching_su_crawler.Geoname.models import GeoCountry, GeoCountryNeighbour, GeoCountryLanguage

def nonempty_cell(cell):
    r = Truecontinent
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
    
    GeoCountry.objects.all().delete()
    GeoCountryNeighbour.objects.all().delete()
    GeoCountryLanguage.objects.all().delete()
    
    file = open("../../geonames/countryInfo.txt")

    COLUMN_COUNT = 18
    
    for line in file:
        if not line.startswith('#'):
            print line
            line = line.strip()
            items = line.split("\t")
            cnt = len(items)
            print items[1], items[4], items[5], items[8], items[11]
            country = GeoCountry(iso=items[0], iso3 = items[1], iso_num = int(items[2]), geoname_id=int(items[16] or 0))
            country.fips = items[3]
            country.name = items[4]
            country.capital = items[5]
            country.area_sqkm = int(round(float(items[6] or 0)))
            country.population = int(items[7] or 0)
            country.continent = items[8]
            country.tld = items[9]
            country.currency_code = items[10]
            country.currency_name = items[11]
            country.save()
            
            languages = items[15].split(',')
            for lang in languages:
                l = GeoCountryLanguage(country_iso3=country.iso3, lang_code=lang)
                l.save()
            
            if cnt == COLUMN_COUNT:
                neighbours = items[-1].split(',')
                for n in neighbours:
                    neighbour = GeoCountryNeighbour(country_iso3=country.iso3, neighbour_iso=n)
                    neighbour.save()

    
    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
