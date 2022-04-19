#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import zipfile
import djyptestutils as yplib
from time import time, strptime
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.main.GeoName.models import GeoCountry
from gpsfun.main.models import log
from gpsfun.main.db_utils import sql2list, sql2val
from lxml import etree as ET
from gpsfun.main.db_utils import execute_query
from DjHDGutils.dbutils import get_object_or_none
from  gpsfun.main.utils import update_geothing, \
      create_new_geothing, TheGeothing, TheLocation

CACHES_PER_PAGE = 500

OCDE_TYPES = {
    'Virt.': 'VI',
    'Trad.': 'TR',
    'Multi': 'MS',
    'Quiz': 'QZ',
    'Other': 'OT',
    'Moving': 'MO',
    'Event': 'EV',
    'ICam.': 'WC',
    'Driv': 'DR',
    'Math': 'MT',
    }
def ocde_timestamp():
    return datetime.now().strftime('%Y%m%d') + '000000'

def main():
    start = time()

    yplib.set_up()
    yplib.set_debugging(False)

    geosite = Geosite.objects.get(code='OCDE')

    countries = GeoCountry.objects.all()
    countries = countries.values_list('iso', flat=True)

    sql = """
    SELECT `value`
    FROM variables
    WHERE `name`='last_ocde_updated'
    """
    lastdate = sql2val(sql);
    if not lastdate:
        lastdate = '20000101000000'
    statuses = []
    types = []
    oc_count = 0
    gc_count = 0
    nc_count = 0

    k = 0
    uc = 0
    nc = 0

    for country in countries:
        url = 'http://opencaching.de/xml/ocxml11.php?modifiedsince=%s&cache=1&country=%s' % \
            (lastdate, country)
        response = urllib2.urlopen(url)
        xml = response.read()
        try:
            root = ET.XML(xml)
        except Exception as e:
            print('PARSING ERROR', country, e)
            continue

        # session id
        current_session = root[0]
        session_id = current_session.text

        # count
        records = root[1]
        caches_count = int(records.get("cache") or 0)
        if caches_count:
            page_count = int(round(caches_count * 1.0 / CACHES_PER_PAGE, 0)) + 1
            for p in range(page_count):
                page_url = 'http://www.opencaching.de/xml/ocxml11.php?sessionid=%s&file=%s' % \
                    (session_id, p + 1)
                page_response = urllib2.urlopen(page_url).read()
                from StringIO import StringIO
                zipdata = StringIO()
                zipdata.write(page_response)
                try:
                    zf = zipfile.ZipFile(zipdata)
                except:
                    continue
                for name in zf.namelist():
                    uncompressed = zf.read(name)
                    cache_root = ET.XML(uncompressed)
                    latitude = None
                    longitude = None
                    status = None
                    created_date_str = ''
                    for cache in  cache_root.getchildren():
                        k += 1
                        if cache.tag == 'cache':
                            the_geothing = TheGeothing()
                            the_location = TheLocation()
                            for param in cache:
                                if param.tag == 'id':
                                    the_geothing.pid = param.get('id')
                                if param.tag == 'userid':
                                    the_geothing.author = param.text
                                if param.tag == 'name':
                                    the_geothing.name = param.text
                                if param.tag == 'longitude':
                                    longitude = param.text
                                if param.tag == 'latitude':
                                    latitude = param.text
                                if param.tag == 'type':
                                    cache_type = param.get('short')
                                    the_geothing.type_code = OCDE_TYPES.get(cache_type)
                                    type_ = (param.get('id'), param.get('short'))
                                    if not type_ in types:
                                        types.append(type_)
                                if param.tag == 'status':
                                    status = int(param.get('id') or 0)
                                    status_ = (status, param.text)
                                    if not status_ in statuses:
                                        statuses.append(status_)
                                if param.tag == 'waypoints':
                                    the_geothing.code = param.get('oc')
                                    if the_geothing.code:
                                        oc_count += 1
                                    gccode = param.get('gccom')
                                    if gccode:
                                        gc_count += 1
                                    nccode = param.get('nccom')
                                    if nccode:
                                        nc_count += 1
                                if param.tag == 'datecreated':
                                    created_date_str = param.text
                                    parts = strptime(created_date_str, '%Y-%m-%d %H:%M:%S')
                                    dt = datetime(parts[0], parts[1], parts[2],
                                                  parts[3], parts[4], parts[5])
                                    the_geothing.created_date = dt

                                if latitude and longitude and status == 1:

                                    the_location.NS_degree = float(latitude)
                                    the_location.EW_degree = float(longitude)
                                    if the_geothing.code and the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                                        geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)
                                        if geothing is not None:
                                            uc += update_geothing(geothing, the_geothing, the_location) or 0
                                        else:
                                            create_new_geothing(the_geothing, the_location, geosite)
                                            nc += 1

    message = 'OK. updated %s, new %s' % (uc, nc)
    log('map_ocde_caches', message)
    print(message)
    sql = """
    UPDATE `variables`
    SET `value`='%s'
    WHERE `name`='last_ocde_updated'
    """ % ocde_timestamp()
    execute_query(sql)

    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
