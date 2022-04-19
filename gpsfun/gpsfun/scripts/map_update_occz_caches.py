#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import djyptestutils as yplib
from time import time, strptime
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.main.models import log
from gpsfun.main.db_utils import sql2list, sql2val
from lxml import etree as ET
from DjHDGutils.dbutils import get_object_or_none
from  gpsfun.main.utils import update_geothing, \
      create_new_geothing, TheGeothing, TheLocation, get_degree

OCCZ_TYPES = {
    'multicache': 'MS',
    u'tradi\u010dn\xed': 'TR',
    u'kv\xedz': 'QZ',
    'event': 'EV',
    u'nezn\xe1m\xe1': 'OT',
    'drive-in': 'DR',
    'webcam': 'WC',
    u'virtu\xe1ln\xed': 'VI',
    u'matematick\xe1': 'MT',
}

def main():
    start = time()

    yplib.set_up()
    yplib.set_debugging(False)

    geosite = Geosite.objects.get(code='OCCZ')

    statuses = []
    types = []
    oc_count = 0

    k = 0
    uc = 0
    nc = 0

    url = 'http://www.opencaching.cz/search.php?searchto=searchbydistance&showresult=1&output=XML&sort=byname&latNS=N&lat_h=50&lat_min=5.123&lonEW=E&lon_h=14&lon_min=20.123&distance=1500&unit=km&count=500&startat=0'

    response = urllib2.urlopen(url).read()

    cache_root = ET.XML(response)

    docinfo = cache_root.getchildren()[0]
    result_count = 0
    for tag in docinfo.getchildren():
        if tag.tag == 'results':
            result_count = int(tag.text or 0)
    if result_count:
        for cache in  cache_root.getchildren()[1:]:
            latitude = None
            longitude = None
            status = None
            created_date_str = ''
            k += 1
            if cache.tag == 'cache':
                the_geothing = TheGeothing()
                the_location = TheLocation()

                for param in cache:
                    if param.tag == 'id':
                        the_geothing.pid = param.text
                    if param.tag == 'owner':
                        the_geothing.author = param.text
                    if param.tag == 'name':
                        the_geothing.name = param.text
                    if param.tag == 'lon':
                        longitude = param.text
                    if param.tag == 'lat':
                        latitude = param.text
                    if param.tag == 'type':
                        cache_type = param.text
                        the_geothing.type_code = OCCZ_TYPES.get(cache_type)
                        if not cache_type in types:
                            types.append(cache_type)
                    if param.tag == 'status':
                        status = param.text
                        if not status in statuses:
                            statuses.append(status)
                    if param.tag == 'waypoint':
                        the_geothing.code = param.text
                        if the_geothing.code:
                            oc_count += 1
                    if param.tag == 'hidden':
                        created_date_str = param.text
                        parts = strptime(created_date_str, '%d.%m.%Y')
                        dt = datetime(parts[0], parts[1], parts[2],
                                      parts[3], parts[4], parts[5])
                        the_geothing.created_date = dt

                if latitude and longitude:

                    the_location.NS_degree = get_degree(latitude)
                    the_location.EW_degree = get_degree(longitude)
                    if the_geothing.code and the_geothing.pid and \
                       the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                        geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)
                        if geothing is not None:
                            uc += update_geothing(geothing, the_geothing, the_location) or 0
                        else:
                            create_new_geothing(the_geothing, the_location, geosite)
                            nc += 1

    message = 'OK. updated %s, new %s' % (uc, nc)
    log('map_occz_caches', message)
    print(message)

    print
    print(types)
    print(statuses)

    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
