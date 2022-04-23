#!/usr/bin/env python
"""
NAME
     map_update_su_caches.py

DESCRIPTION
     Updates list of caches from geocaching.su
"""

import re
from datetime import datetime
import requests
from lxml import etree as ET

from django.core.management.base import BaseCommand

from gpsfun.main.models import log
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite
from gpsfun.main.db_utils import get_object_or_none
from gpsfun.geocaching_su_stat.utils import LOGIN_DATA
from gpsfun.main.utils import (
    update_geothing, create_new_geothing, TheGeothing, TheLocation)


class Command(BaseCommand):
    """ command """
    help = 'Updates list of caches from geocaching.su'

    def handle(self, *args, **options):
        url = 'http://www.geocaching.su/rss/geokrety/api.php?interval=1y&ctypes=1,2,3,7&changed=1'
        with requests.Session() as session:
            xml = session.get(url, data=LOGIN_DATA).content

        try:
            sxml = ET.XML(xml)
        except Exception as exception:
            print(type(exception))
            print(exception)
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
                        date_[2] = date_[2].split()[0]
                        if len(date_) == 3:
                            the_geothing.created_date = datetime(
                                int(date_[0]), int(date_[1]), int(date_[2]))
                if the_geothing.code:
                    preg = re.compile('(\D+)(\d+)')
                    dgs = preg.findall(the_geothing.code)
                    if dgs:
                        code_data = dgs[0]
                        the_geothing.pid = int(code_data[1])
                        the_geothing.type_code = code_data[0]

                if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
                    geothing = get_object_or_none(
                        Geothing, pid=the_geothing.pid, geosite=geosite)
                if geothing is not None:
                    cnt_upd += update_geothing(geothing, the_geothing, the_location) or 0

                else:
                    create_new_geothing(the_geothing, the_location, geosite)
                    cnt_new += 1

        message = f'OK {cnt_new}/{cnt_upd}'
        log('map_gcsu_caches', message)
        print(message)

        return 'List of caches from geocaching.su has updated'
