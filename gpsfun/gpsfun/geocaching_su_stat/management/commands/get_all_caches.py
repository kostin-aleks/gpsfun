#!/usr/bin/env python
"""
NAME
     get_all_caches.py

DESCRIPTION
     Loads list of all caches with ISO codes and updates db table
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UpdateType
from gpsfun.geocaching_su_stat.utils import (
    LOGIN_DATA, logged, get_caches
)


class Command(BaseCommand):
    """ Command """
    help = 'Loads list of all caches'

    def handle(self, *args, **options):
        with requests.Session() as session:
            session.post(
                'https://geocaching.su',
                data=LOGIN_DATA
            )

            response = session.get('https://geocaching.su')
            if not logged(response.text):
                print('Authorization failed')
            else:
                get_caches()

        log(UpdateType.gcsu_caches, 'OK')

        return 'List of caches has updated'
