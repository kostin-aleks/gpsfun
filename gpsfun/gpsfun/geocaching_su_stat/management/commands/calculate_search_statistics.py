#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     calculate_search_statistics.py

DESCRIPTION
     Calculates search statistics
"""
import os
from datetime import date
from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import Cach, CachStat
from gpsfun.main.models import log, UPDATE_TYPE


def patch_it(sql):
    sql = sql.strip()

    with connection.cursor() as cursor:
        print('execute', sql)
        cursor.execute(sql)


class Command(BaseCommand):
    help = 'Calculates search statistics by sql queries'

    def handle(self, *args, **options):

        for cache in Cach.objects.exclude(author__isnull=True):
            cache_stat, created = CachStat.objects.get_or_create(
                cach=cache,
                cach_pid=cache.pid,
                geocacher=cache.author
            )
            cache_stat.calculate_points()


        queries = [
            """
            insert into geocacher_search_stat
            (geocacher_id, geocacher_uid, country, region)
            select g.id, g.uid, c.name, gcs.name
            from geocacher g
            left join geocacher_search_stat gss
                on g.uid = gss.geocacher_uid
            left join geo_country c
                on g.country_iso3 = c.iso3
            left join geo_country_subject gcs
                on c.iso = gcs.country_iso and g.admin_code = gcs.code
            where gss.geocacher_uid is null
            """,

            """
             update geocacher_search_stat gss
             set
             points=(
                 select ROUND(sum(IFNULL(cs.points, 0))) as points_sum
                 from  log_seek_cach lsc
                 left join cach_stat cs on lsc.cach_pid = cs.cach_pid
                 where lsc.cacher_uid = gss.geocacher_uid
             ),
             year_points=(
                 select ROUND(sum(IFNULL(cs.points, 0))) as points_sum
                 from  log_seek_cach lsc
                 left join cach_stat cs on lsc.cach_pid = cs.cach_pid
                 where YEAR(lsc.found_date)=%s and
                       lsc.cacher_uid = gss.geocacher_uid
             )
         """ % date.today().year
        ]
        for sql in queries:
            patch_it(sql)

        log(UPDATE_TYPE.search_statistics, 'OK')

        return 'Geocachers search statistics is updated'
