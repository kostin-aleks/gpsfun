#!/usr/bin/env python
"""
NAME
     patch_caches.py

DESCRIPTION
     Patch caches data by sql queries
"""
import os
from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UpdateType


def patch_it(name):
    """ patch sql queries """
    pathtofile = os.path.join(settings.SCRIPTS_ROOT, name)
    with open(pathtofile, 'r') as f:
        text = f.read()
        queries = text.split(';')
        for sql in queries:
            sql = sql.strip()

            if sql.startswith('SELECT') or sql.startswith('select') \
               or not sql or sql.startswith('--') or sql.startswith('#'):
                continue

            print
            print('execute', sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
        f.close()


class Command(BaseCommand):
    """ Command """
    help = 'Patch caches data by sql queries'

    def handle(self, *args, **options):

        sql_batches = (
            'set_cach_country_code.sql',
            'set_cach_oblast_code.sql',
        )

        for name in sql_batches:
            patch_it('sql/' + name)
            print(name, ' processed')

        log(UpdateType.geocacher_patch, 'OK')

        return 'Geocachers data are updated'
