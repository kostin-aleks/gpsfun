#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     get_all_caches.py

DESCRIPTION
     Loads list of all caches with ISO codes and updates db table
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches
)


class Command(BaseCommand):
    help = 'Loads list of all caches'

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
                get_caches()

        log(UPDATE_TYPE.gcsu_caches, 'OK')

        return 'List of caches has updated'
