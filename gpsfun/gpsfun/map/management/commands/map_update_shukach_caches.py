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
from pprint import pprint
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.db_utils import sql2table, sql2val, execute_query, get_cursor
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location
from gpsfun.DjHDGutils.dbutils import get_object_or_none, exec_sql
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
                ids = range(k * 1000, (k + 1) * 1000)
                ids_str = ','.join([str(id) for id in ids])
                url = 'https://www.shukach.com/export_wpt'
                r = session.post(
                    url,
                    data={'wptnids': ids_str}).text
                wpt = r.split('\n')
                print(k, len(wpt))
                if len(wpt) < 6:
                    continue

                for point in wpt:
                    # print(point)
                    # print
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

        sql = "SELECT id FROM geosite WHERE code='SHUKACH'"
        shukach_id = sql2val(sql)

        # update existent geothings
        sql = """
        UPDATE geothing gt
             LEFT JOIN _temp_geothing as t
             ON gt.pid=t.pid
        SET gt.created_date=t.created_date,
            gt.name=t.name,
            gt.author=t.author,
            gt.type_code=t.type_code
        WHERE gt.geosite_id={} AND
            t.code IS NOT NULL AND
            (gt.name != t.name OR
            gt.author != t.author OR
            gt.type_code != t.type_code)
        """.format(shukach_id)
        #print sql
        updated_things = exec_sql(sql)

        sql = """
        UPDATE location as l
            LEFT JOIN geothing as gt ON l.id=gt.location_id
            LEFT JOIN _temp_geothing as t
             ON gt.pid=t.pid
        SET l.NS_degree=t.NS_degree,
            l.EW_degree=t.EW_degree
        WHERE gt.geosite_id={} AND
            t.code IS NOT NULL AND
            ((ABS(l.NS_degree - t.NS_degree) > 0.00001) OR
             (ABS(l.EW_degree - t.EW_degree) > 0.00001))
        """.format(shukach_id)
        updated_points = exec_sql(sql)

        # list of id of removed geothings
        sql = """
        SELECT gt.id
        FROM geothing gt
             LEFT JOIN _temp_geothing as t
             ON gt.pid=t.pid
        WHERE gt.geosite_id={} AND t.code IS NULL
        """.format(shukach_id)
        removed = sql2table(sql)

        new_count = 0
        # insert new geothings
        sql = """
        SELECT t.pid, t.code, t.name, t.created_date, t.author,
               t.country_code, t.type_code, t.NS_degree, t.EW_degree
        FROM _temp_geothing as t
             LEFT JOIN geothing gt ON gt.pid=t.pid AND gt.geosite_id={}
        WHERE gt.pid IS NULL
        """.format(shukach_id)
        cursor = get_cursor(sql)
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            else:
                sql = """
                INSERT INTO location
                (NS_degree, EW_degree)
                VALUES
                ({}, {})
                """.format(row[7], row[8])

                execute_query(sql)
                sql = "SELECT LAST_INSERT_ID()"
                location_id = sql2val(sql)

                sql = """
                INSERT INTO geothing
                (geosite_id, pid, code, name, created_date, author,
                type_code, location_id, admin_code)
                SELECT {}, t.pid, t.code, t.name, t.created_date, t.author,
                t.type_code, {}, '777'
                FROM _temp_geothing as t
                WHERE t.pid={}
                """.format(shukach_id, location_id, row[0])
                execute_query(sql)
                new_count += 1


        message = 'OK. %s waypoints, updated %s waypoints, updated %s locations, new %s, removed %s' % (
            all_points_count,
            updated_things or 0,
            updated_points or 0,
            new_count,
            len(removed))
        print(message)
        log('map_shukach', message)


        return 'List of caches from geocaching.su has updated'

