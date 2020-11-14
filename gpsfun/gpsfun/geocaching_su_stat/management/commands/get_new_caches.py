#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     get_new_caches.py

DESCRIPTION
     Loads list of new caches with ISO codes and updates db table
"""

import requests
from django.core.management.base import BaseCommand
from django.db.models import Max
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches
)
from gpsfun.main.GeoCachSU.models import Cach


class Command(BaseCommand):
    help = 'Loads list of new caches'

    def handle(self, *args, **options):
        with requests.Session() as session:
            post = session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )

            r = session.get('https://geocaching.su')

            if not logged(r.text):
                print('Authorization failed')
            else:
                last_cid = Cach.objects.all().aggregate(
                    last_pid=Max('pid'))['last_pid']
                get_caches(last_cid)

        log(UPDATE_TYPE.gcsu_new_caches, 'OK')

        return 'List of caches has updated'
