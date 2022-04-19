#!/usr/bin/env python
# -*- coding: utf-8 -*-

import djyptestutils as yplib
from time import time
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.main.models import log
from lxml import etree as ET
import urllib2
from DjHDGutils.dbutils import get_object_or_none
from  gpsfun.main.utils import update_geothing, \
      create_new_geothing, TheGeothing, TheLocation, get_degree

def main():
    LOAD_CACHES = True

    start = time()

    yplib.set_up()
    yplib.set_debugging(False)

    url = 'http://www.geocaching.su/rss/geokrety/api.php?interval=1y&ctypes=1,2,3,7&changed=1'

    f = urllib2.urlopen(url)
    xml = f.read()
    xml = xml

    try:
        sxml = ET.XML(xml)
    except Exception as e:
        print(type(e))
        print(e)
        return

    cnt_new = 0
    cnt_upd = 0
    caches = sxml.getchildren()

    geosite = Geosite.objects.get(code='GC_SU')

    for cache in caches:
        if cache.tag == 'cache':
            the_geothing = TheGeothing()
            the_location = TheLocation()
            for tag_ in cache.getchildren():
                if tag_.tag == 'code':
                    the_geothing.code = tag_.text
                if tag_.tag == 'autor':
                    the_geothing.author = tag_.text
                if tag_.tag == 'name':
                    the_geothing.name = tag_.text
                if tag_.tag == 'position':
                    lat_degree = float(tag_.get('lat'))
                    the_location.NS_degree = lat_degree
                    lon_degree = float(tag_.get('lon'))
                    the_location.EW_degree = lon_degree
                if tag_.tag == 'cdate':
                    date_str = tag_.text
                    date_ = date_str.split('-')
                    if len(date_) == 3:
                        the_geothing.created_date = datetime(int(date_[0]), int(date_[1]), int(date_[2]))
            if  the_geothing.code:
                p = re.compile('(\D+)(\d+)')
                dgs = p.findall(the_geothing.code)
                if dgs:
                    code_data = dgs[0]
                    the_geothing.pid = int(code_data[1])
                    the_geothing.type_code = code_data[0]

            if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)
                if geothing is not None:
                    cnt_upd += update_geothing(geothing, the_geothing, the_location) or 0

                else:
                    create_new_geothing(the_geothing, the_location, geosite)
                    cnt_new += 1

    message = 'OK %s/%s'%(cnt_new, cnt_upd)
    log('map_gcsu_caches', message)
    print(message)
    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
