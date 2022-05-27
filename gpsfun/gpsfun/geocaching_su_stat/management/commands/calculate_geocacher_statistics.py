#!/usr/bin/env python
"""
NAME
     calculate_geocacher_statistics.py

DESCRIPTION
     Calculates geocachers statistics
"""
import os
from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UpdateType


def patch_it(name):
    """ patch sql queries from file with name """
    pathtofile = os.path.join(settings.SCRIPTS_ROOT, name)
    with open(pathtofile, 'r', encoding="utf-8") as f:
        text = f.read()
        queries = text.split(';')
        for sql in queries:
            sql = sql.strip()

            if sql.startswith('SELECT') or sql.startswith('select') \
               or not sql or sql.startswith('--') or sql.startswith('#'):
                continue

            with connection.cursor() as cursor:
                virtual = "'VI', 'CT', 'EV', 'LV', 'MV'"
                if '%s' in sql:
                    sql = sql % virtual
                print('execute', sql)
                cursor.execute(sql)
        f.close()


class Command(BaseCommand):
    """ Command """
    help = 'Calculates geocachers statistics by sql queries'

    def handle(self, *args, **options):
        """ handle """
        sql_batches = (
            'sql/calculate_geocacher_statistics.sql',
        )
        for name in sql_batches:
            patch_it(name)
            print(name, ' processed')

        log(UpdateType.geocacher_statistics, 'OK')

        return 'Geocachers statistics is updated'
