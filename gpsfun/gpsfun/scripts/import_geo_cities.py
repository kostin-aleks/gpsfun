#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
import codecs
from datetime import datetime
from DjHDGutils.misc import atoi
from gpsfun.main.GeoName.models import GeoCity

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
    
    GeoCity.objects.all().delete()
    file = codecs.open("/tmp/cities1000.txt", "r", "utf-8")

    for line in file:
        line = line.encode('utf-8')
        items = line.split("\t")

        geo_city = GeoCity(geonameid=atoi(items[0]),
                           name=items[1],
                           asciiname=items[2],
                           alternatenames=items[3],
                           latitude=float(items[4]),
                           longitude=float(items[5]),
                           fclass=items[6],
                           fcode=items[7],
                           country=items[8],
                           cc2=items[9],
                           admin1=items[10],
                           admin2=items[11],
                           admin3=items[12],
                           admin4=items[13],
                           population=atoi(items[14]),
                           elevation=atoi(items[15]),
                           gtopo30=atoi(items[16]),
                           timezone=items[17], 
                           moddate=date_or_none(items[18])
                           )
        try:
            geo_city.save()
        except:
            geo_city.alternatenames = ''
            geo_city.save()
        #print geo_city.geonameid, geo_city.name,  geo_city.moddate

    elapsed = time() - start
    print "Elapsed time -->", elapsed

if __name__ == '__main__':
    main()
