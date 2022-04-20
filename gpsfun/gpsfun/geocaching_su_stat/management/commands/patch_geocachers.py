#!/usr/bin/env python
"""
NAME
     patch_geocachers.py

DESCRIPTION
     Patch geocachers data by sql queries
"""
import os
import requests
from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from gpsfun.main.GeoCachSU.models import Geocacher
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_found_caches_countries, set_country_code,
    get_found_caches_oblast, set_oblast_code)


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
    help = 'Patch geocachers data by sql queries'

    def handle(self, *args, **options):

        sql_batches = (
            'set_country_iso_for_geocachers.sql',
            'set_admin_code_to_geocacher.sql',
            'crimea.sql'
        )

        for name in sql_batches:
            patch_it('sql/' + name)
            print(name, ' processed')

        with requests.Session() as session:
            session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )
        response = session.get('https://geocaching.su')
        if not logged(response.text):
            print('Authorization failed')
        else:
            for uid in Geocacher.objects.filter(
                    country_iso3__isnull=True).values_list('uid', flat=True):
                response = session.get(
                    'http://www.geocaching.su/site/popup/userstat.php',
                    params={'s': 2, 'uid': uid}
                )
                country = get_found_caches_countries(uid, response.text)
                set_country_code(uid, country)
            names = {''}
            for uid in Geocacher.objects.filter(
                    admin_code__isnull=True).values_list('uid', flat=True):
                response = session.get(
                    'http://www.geocaching.su/site/popup/userstat.php',
                    params={'s': 2, 'uid': uid}
                )
                oblast = get_found_caches_oblast(uid, response.text)
                names.add(oblast)
                set_oblast_code(uid, oblast)


        log(UPDATE_TYPE.geocacher_patch, 'OK')

        return 'Geocachers data are updated'
