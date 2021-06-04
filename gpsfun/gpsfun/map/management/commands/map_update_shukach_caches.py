#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     map_update_shukach_caches.py

DESCRIPTION
     Updates list of caches from shukach.com
"""

import re
import requests
# import djyptestutils as yplib
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.db_utils import sql2table, sql2val, execute_query, get_cursor
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from lxml import etree as ET
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches
)
from  gpsfun.main.utils import (
    update_geothing, create_new_geothing, TheGeothing, TheLocation, get_degree)


def Dephi_date_to_python_date(d):
    days = int(d)
    hours = int(round((d - days)*24))
    date_ = datetime(1899, 12, 30) + timedelta(days=int(d), hours=hours)
    return date_

WPT_CODE = 1
WPT_LAT = 2
WPT_LON = 3
WPT_TITLE = 10
WPT_DATE = 4


class Command(BaseCommand):
    help = 'Updates list of caches from shukach.com'

    def handle(self, *args, **options):
        url = 'https://www.shukach.com/ru/karta?destination=karta'

        with requests.Session() as session:
            r = session.post(
                url,
                data={
                    'name': 'gps-fun',
                    'pass': 'vjlthybpfwbzwbz',
                    'form_id': 'user_login_block',
                }).text
            if not 'gps-fun' in r:
                print('Autorization failed')
                return

            sql = """
            DELETE FROM _temp_geothing
            """
            execute_query(sql)

            all_points_count = 0
            updated_things = 0
            updated_points = 0
            new_count = 0
            removed = []

            geosite = Geosite.objects.get(code='SHUKACH')

            for k in range(100):
                print(k)
                ids = range(k * 1000, (k + 1) * 1000)
                ids_str = ','.join([str(id) for id in ids])
                url = 'https://www.shukach.com/export_wpt'
                r = session.post(
                    url,
                    data={'wptnids': ids_str}).text
                wpt = r.split('\n')

                if len(wpt) < 6:
                    continue
                for point in wpt[:20]:
                    pid = code = None
                    name = ''
                    created_date = None
                    author = type_code = ''
                    NS_degree = EW_degree = None

                    fields = point.split(',')

                    if len(fields) > WPT_TITLE and fields[0].isdigit():
                        all_points_count += 1
                        p = re.compile('(\D+)(\d+)')
                        code = fields[WPT_CODE]
                        dgs = p.findall(code)
                        if dgs:
                            type_code = dgs[0][0]
                            pid = int(dgs[0][1])
                            if type_code in GEOCACHING_ONMAP_TYPES:
                                NS_degree = float(fields[WPT_LAT])
                                EW_degree = float(fields[WPT_LON])
                                p = re.compile(r'(.+)от(.+)')
                                dgs = p.findall(fields[WPT_TITLE])
                                if dgs:
                                    title = dgs[0]
                                    name = title[0].strip()
                                    author = title[1].strip()
                                else:
                                    name = fields[WPT_TITLE]
                                d = float(fields[WPT_DATE])
                                created_date = Dephi_date_to_python_date(d)
                                date_str = created_date.strftime('%Y-%m-%d %H:%M')
                                ns_str = '{0:.9}'.format(NS_degree)
                                ew_str = '{0:.9}'.format(EW_degree)
                                sql = """
                                INSERT INTO _temp_geothing
                                (pid, code, name, created_date, author,
                                type_code, NS_degree, EW_degree)
                                VALUES
                                ({},'{}','{}','{}', '{}', '{}', {}, {})
                                """.format(
                                    pid, code,
                                    name.replace("'", "\\'"),
                                    date_str, author,
                                    type_code,
                                    ns_str, ew_str)
                                execute_query(sql)

                # break

        message = 'OK. %s waypoints, updated %s waypoints, updated %s locations, new %s, removed %s' % (
            all_points_count,
            updated_things or 0,
            updated_points or 0,
            new_count,
            len(removed))
        print(message)
        log('map_shukach', message)


        return 'List of caches from geocaching.su has updated'

