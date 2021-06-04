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
        call_command('set_cache_autor')
        call_command('patch_geocachers')
        call_command('patch_caches')
        call_command('set_cach_grades')
        call_command('set_cach_location')
        # call_command('set_geocacher_location')
        call_command('check_data')


