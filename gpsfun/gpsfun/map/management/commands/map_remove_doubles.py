#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     map_remove_doubles.py

DESCRIPTION
     Removes double of caches
"""

import json
import re
import requests
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.db_utils import sql2table, sql2val, execute_query, get_cursor
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import (
    Geothing, Geosite, Location, BlockNeedBeDivided)
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from lxml import etree as ET
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches
)
from  gpsfun.main.utils import (
    update_geothing, create_new_geothing, TheGeothing, TheLocation, get_degree)


def process(double):

    code, count = double
    if count >= 2:
        things = Geothing.objects.filter(code=code).order_by('pid')
        found = []
        for thing in things:
            s = thing.code[2:]

            hex_pid = int(s, 16)
            if thing.pid == hex_pid:
                found.append(thing.id)

        if found:
            Geothing.objects.filter(code=code).exclude(id__in=found).delete()
        else:
            print('exception', double)

    else:
        print(double)


class Command(BaseCommand):
    help = 'Removes double of caches'

    def handle(self, *args, **options):
        sql = """
            select g.code as code, count(g.id) as cnt
            from geothing g
            JOIN geosite gs ON g.geosite_id = gs.id
            WHERE gs.code = 'OCPL'
            group by g.code
            having cnt > 1
            """
        doubled = sql2table(sql)

        if len(doubled):
            print('count of doubles:', len(doubled))
            for item in doubled:
                process(item)
            message = 'Doubles of caches are removed'
        else:
            message = 'No double caches'
        return

