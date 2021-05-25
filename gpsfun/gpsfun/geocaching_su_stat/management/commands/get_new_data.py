#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     get_new_data.py

DESCRIPTION
     Loads new data and updates db table
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Loads new data'

    def handle(self, *args, **options):
        call_command('get_new_caches')
        call_command('get_new_geocachers')
        call_command('get_new_log_created')
        call_command('get_new_log_found')
        call_command('get_new_log_recommended')


