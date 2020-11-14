#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from gpsfun.main.models import log, UPDATE_TYPE


def patch_it(name):
    pathtofile = os.path.join(settings.SCRIPTS_ROOT, name)
    f = open(pathtofile, 'r')
    text = f.read()
    queries = text.split(';')
    for sql in queries:
        sql = sql.strip()

        if sql.startswith('SELECT') or sql.startswith('select') \
           or not sql or sql.startswith('--') or sql.startswith('#'):
            continue
        else:
            with connection.cursor() as cursor:
                virtual = "'VI', 'CT', 'EV', 'LV', 'MV'"
                if '%s' in sql:
                    sql = sql % virtual
                print('execute', sql)
                cursor.execute(sql)


class Command(BaseCommand):
    help = 'Calculates geocachers statistics by sql queries'

    def handle(self, *args, **options):

        sql_batches = (
            'sql/calculate_geocacher_statistics.sql',
        )
        for name in sql_batches:
            patch_it(name)
            print(name, ' processed')

        log(UPDATE_TYPE.geocacher_statistics, 'OK')

        return 'Geocachers statistics is updated'
