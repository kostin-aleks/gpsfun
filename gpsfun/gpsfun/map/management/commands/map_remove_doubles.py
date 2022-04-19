#!/usr/bin/env python
"""
NAME
     map_remove_doubles.py

DESCRIPTION
     Removes double of caches
"""

from django.core.management.base import BaseCommand

from gpsfun.main.db_utils import sql2table
from gpsfun.main.GeoMap.models import Geothing


def process(double):
    """ process """
    code, count = double
    if count >= 2:
        things = Geothing.objects.filter(code=code).order_by('pid')
        found = []
        for thing in things:
            string = thing.code[2:]

            hex_pid = int(string, 16)
            if thing.pid == hex_pid:
                found.append(thing.id)

        if found:
            Geothing.objects.filter(code=code).exclude(id__in=found).delete()
        else:
            print('exception', double)

    else:
        print(double)


class Command(BaseCommand):
    """ Command """
    help = 'Removes double of caches'

    def handle(self, *args, **options):
        """ handle """
        sql = """
            select g.code as code, count(g.id) as cnt
            from geothing g
            JOIN geosite gs ON g.geosite_id = gs.id
            WHERE gs.code = 'OCPL'
            group by g.code
            having cnt > 1
            """
        doubled = sql2table(sql)

        if doubled:
            print('count of doubles:', len(doubled))
            for item in doubled:
                process(item)
            message = 'Doubles of caches are removed'
        else:
            message = 'No double caches'
        return message
