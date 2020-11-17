#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     check_data.py

DESCRIPTION
     Checks caches and geocachers
"""

import requests
from django.core.management.base import BaseCommand
from gpsfun.main.models import log, UPDATE_TYPE
from gpsfun.main.models import LogCheckData


class Command(BaseCommand):
    help = 'Checks caches and geocachers'

    def handle(self, *args, **options):
        LogCheckData.check_data()

        log(UPDATE_TYPE.gcsu_check_data, 'OK')

        return 'Result of checking is saved'
