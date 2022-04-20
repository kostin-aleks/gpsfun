#!/usr/bin/env python
"""
NAME
     check_data.py

DESCRIPTION
     Checks caches and geocachers
"""

from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.models import LogCheckData


class Command(BaseCommand):
    """ Command """
    help = 'Checks caches and geocachers'

    def handle(self, *args, **options):
        """ handle """
        LogCheckData.check_data()

        log(UPDATE_TYPE.gcsu_check_data, 'OK')

        return 'Result of checking is saved'
