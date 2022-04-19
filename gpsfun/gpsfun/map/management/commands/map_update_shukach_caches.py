#!/usr/bin/env python
"""
NAME
     map_update_shukach_caches.py

DESCRIPTION
     Updates list of caches from shukach.com
"""

import re
from datetime import datetime, timedelta
import requests

from django.core.management.base import BaseCommand

from gpsfun.main.models import log
from gpsfun.main.db_utils import sql2table, sql2val, execute_query, get_cursor
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.DjHDGutils.dbutils import exec_sql


def dephi_date_to_python_date(date):
    """ convert Delphi into python date """
    days = int(date)
    hours = int(round((date - days) * 24))
    date_ = datetime(1899, 12, 30) + timedelta(days=int(date), hours=hours)
    return date_


WPT_CODE = 1
WPT_LAT = 2
WPT_LON = 3
WPT_TITLE = 10
WPT_DATE = 4


class Command(BaseCommand):
    """ command """
    help = 'Updates list of caches from shukach.com'

    def handle(self, *args, **options):
        """ handle """
        url = 'https://www.shukach.com/ru/karta?destination=karta'

        with requests.Session() as session:
            result = session.post(
                url,
                data={
                    'name': 'gps-fun',
                    'pass': 'vjlthybpfwbzwbz',
                    'form_id': 'user_login_block',
                }).text
            if not 'gps-fun' in result:
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

            # geosite = Geosite.objects.get(code='SHUKACH')

            for counter in range(100):
                ids = range(counter * 1000, (counter + 1) * 1000)
                ids_str = ','.join([str(id) for id in ids])
                url = 'https://www.shukach.com/export_wpt'
                result = session.post(
                    url,
                    data={'wptnids': ids_str}).text
                wpt = result.split('\n')
                print(counter, len(wpt))
                if len(wpt) < 6:
                    continue

                for point in wpt:
                    pid = code = None
                    name = ''
                    created_date = None
                    author = type_code = ''
                    ns_degree = ew_degree = None

                    fields = point.split(',')

                    if len(fields) > WPT_TITLE and fields[0].isdigit():
                        all_points_count += 1
                        preg = re.compile('(\D+)(\d+)')
                        code = fields[WPT_CODE]
                        dgs = preg.findall(code)
                        if dgs:
                            type_code = dgs[0][0]
                            pid = int(dgs[0][1])
                            if type_code in GEOCACHING_ONMAP_TYPES:
                                ns_degree = float(fields[WPT_LAT])
                                ew_degree = float(fields[WPT_LON])
                                preg = re.compile(r'(.+)от(.+)')
                                dgs = preg.findall(fields[WPT_TITLE])
                                if dgs:
                                    title = dgs[0]
                                    name = title[0].strip()
                                    author = title[1].strip()
                                else:
                                    name = fields[WPT_TITLE]
                                date = float(fields[WPT_DATE])
                                created_date = dephi_date_to_python_date(date)
                                date_str = created_date.strftime('%Y-%m-%d %H:%M')
                                ns_str = '{0:.9}'.format(ns_degree)
                                ew_str = '{0:.9}'.format(ew_degree)
                                name_ = name.replace("'", "\\'")

                                sql = f"""
                                INSERT INTO _temp_geothing
                                (pid, code, name, created_date, author,
                                type_code, NS_degree, EW_degree)
                                VALUES
                                ({pid},'{code}','{name_}','{date_str}', '{author}',
                                 '{type_code}', {ns_str}, {ew_str})
                                """
                                execute_query(sql)

        sql = "SELECT id FROM geosite WHERE code='SHUKACH'"
        shukach_id = sql2val(sql)

        # update existent geothings
        sql = f"""
        UPDATE geothing gt
             LEFT JOIN _temp_geothing as t
             ON gt.pid=t.pid
        SET gt.created_date=t.created_date,
            gt.name=t.name,
            gt.author=t.author,
            gt.type_code=t.type_code
        WHERE gt.geosite_id={shukach_id} AND
            t.code IS NOT NULL AND
            (gt.name != t.name OR
            gt.author != t.author OR
            gt.type_code != t.type_code)
        """
        #print sql
        updated_things = exec_sql(sql)

        sql = f"""
        UPDATE location as l
            LEFT JOIN geothing as gt ON l.id=gt.location_id
            LEFT JOIN _temp_geothing as t
             ON gt.pid=t.pid
        SET l.NS_degree=t.NS_degree,
            l.EW_degree=t.EW_degree
        WHERE gt.geosite_id={shukach_id} AND
            t.code IS NOT NULL AND
            ((ABS(l.NS_degree - t.NS_degree) > 0.00001) OR
             (ABS(l.EW_degree - t.EW_degree) > 0.00001))
        """
        updated_points = exec_sql(sql)

        # list of id of removed geothings
        sql = f"""
        SELECT gt.id
        FROM geothing gt
             LEFT JOIN _temp_geothing as t
             ON gt.pid=t.pid
        WHERE gt.geosite_id={shukach_id} AND t.code IS NULL
        """
        removed = sql2table(sql)

        new_count = 0
        # insert new geothings
        sql = f"""
        SELECT t.pid, t.code, t.name, t.created_date, t.author,
               t.country_code, t.type_code, t.NS_degree, t.EW_degree
        FROM _temp_geothing as t
             LEFT JOIN geothing gt ON gt.pid=t.pid AND gt.geosite_id={shukach_id}
        WHERE gt.pid IS NULL
        """
        cursor = get_cursor(sql)
        while True:
            row = cursor.fetchone()
            if row is None:
                break

            sql = f"""
            INSERT INTO location
            (NS_degree, EW_degree)
            VALUES
            ({row[7]}, {row[8]})
            """

            execute_query(sql)
            sql = "SELECT LAST_INSERT_ID()"
            location_id = sql2val(sql)

            sql = f"""
            INSERT INTO geothing
            (geosite_id, pid, code, name, created_date, author,
            type_code, location_id, admin_code)
            SELECT {shukach_id}, t.pid, t.code, t.name, t.created_date, t.author,
            t.type_code, {location_id}, '777'
            FROM _temp_geothing as t
            WHERE t.pid={row[0]}
            """
            execute_query(sql)
            new_count += 1

        message = f'OK. {all_points_count} waypoints, updated {updated_things or 0} waypoints, updated {updated_points or 0} locations, new {new_count}, removed {len(removed)}'
        print(message)
        log('map_shukach', message)

        return 'List of caches from geocaching.su has updated'
