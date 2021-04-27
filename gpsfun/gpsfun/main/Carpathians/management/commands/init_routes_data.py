#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
     init_routes_data.py

DESCRIPTION
     Add init data
"""

from django.core.management.base import BaseCommand
from urllib.request import urlopen
from gpsfun.main.Carpathians.models import Ridge, Peak, GeoPoint


class Command(BaseCommand):
    help = 'Adds initial data into database'

    def handle(self, *args, **options):
        items = [
            {'slug': 'chernogora', 'name': 'Черногорский хребет'},
            {'slug': 'marmarosh', 'name': 'Мармарошский хребет'},
            {'slug': 'svidovets', 'name': 'Свидовецкий хребет'},
            {'slug': 'gorgany', 'name': 'Горганы'}]
        for item in items:
            ridge, created = Ridge.objects.get_or_create(
                slug=item['slug'])
            ridge.name = item['name']
            ridge.save()

        items = [
            {'slug': 'bliznitsa', 'name': 'Близница',
                'ridge': 'svidovets', 'height': 1881,
                'point': {'lat': '48 13 18', 'lon': '24 13 57'}},
            {'slug': 'brebeneskul', 'name': 'Бребенескул',
                'ridge': 'chernogora', 'height': 2035,
                'point': {'lat': '48 05 54', 'lon': '24 34 50'}},
            {'slug': 'breskul', 'name': 'Брескул',
                'ridge': 'chernogora', 'height': 1911,
                'point': {'lat': '48 09 01', 'lon': '24 30 42'}},
            {'slug': 'hoverla', 'name': 'Говерла',
                'ridge': 'chernogora', 'height': 2061,
                'point': {'lat': '48 09 36', 'lon': '24 30 00'}},
            {'slug': 'hutyn-tomnatyk', 'name': 'Гутин Томнатик',
                'ridge': 'chernogora', 'height': 2016,
                'point': {'lat': '48 05 59', 'lon': '24 33 24'}},
            {'slug': 'igrovets', 'name': 'Игровец',
                'ridge': 'gorgany', 'height': 1814,
                'point': {'lat': '48 35 52', 'lon': '24 05 58'}},
            {'slug': 'syvulja', 'name': 'Сивуля',
                'ridge': 'gorgany', 'height': 1836,
                'point': {'lat': '48 32 57', 'lon': '24 07 12'}},
            {'slug': 'petros', 'name': 'Петрос',
                'ridge': 'chernogora', 'height': 2020,
                'point': {'lat': '48 10 19', 'lon': '24 25 16'}},
            {'slug': 'petrosul', 'name': 'Петросул',
                'ridge': 'chernogora', 'height': 1855,
                'point': {'lat': '48 10 50', 'lon': '24 25 04'}},
            {'slug': 'sheshul', 'name': 'Шешул',
                'ridge': 'chernogora', 'height': 1726,
                'point': {'lat': '48 09 01', 'lon': '24 22 00'}},
            {'slug': 'pozhezhevska', 'name': 'Пожижевская',
                'ridge': 'chernogora', 'height': 1822,
                'point': {'lat': '48 08 40', 'lon': '24 31 25'}},
            {'slug': 'pop-ivan', 'name': 'Поп Иван',
                'ridge': 'chernogora', 'height': 2020,
                'point': {'lat': '48 02 50', 'lon': '24 37 40'}},
            {'slug': 'pop-ivan-marmarosh', 'name': 'Поп Иван Мармарошский',
                'ridge': 'marmarosh', 'height': 1937,
                'point': {'lat': '47 55 26', 'lon': '24 19 41'}},
            {'slug': 'sherban', 'name': 'Шербан',
                'ridge': 'marmarosh', 'height': 1793,
                'point': {'lat': '47 54 419', 'lon': '24 25 16'}},
            {'slug': 'rebra', 'name': 'Ребра',
                'ridge': 'chernogora', 'height': 2001,
                'point': {'lat': '48 06 40', 'lon': '24 33 32'}},
            {'slug': 'turkul', 'name': 'Туркул',
                'ridge': 'chernogora', 'height': 1933,
                'point': {'lat': '48 07 25', 'lon': '24 31 50'}},
            {'slug': 'dantsyzh', 'name': 'Данциж',
                'ridge': 'chernogora', 'height': 1850,
                'point': {'lat': '48 08 08', 'lon': '24 31 54'}},
            {'slug': 'shpytsi', 'name': 'Шпицы',
                'ridge': 'chernogora', 'height': 1863,
                'point': {'lat': '48 07 33', 'lon': '24 34 03'}},
            {'slug': 'rypa', 'name': 'Рыпа',
                'ridge': 'marmarosh', 'height': 1872,
                'point': {'lat': '47 55 06', 'lon': '24 20 19'}},
        ]
        for item in items:
            ridge = Ridge.objects.get(slug=item['ridge'])
            peak, created = Peak.objects.get_or_create(
                slug=item['slug'], ridge=ridge)
            peak.name = item['name']
            peak.height = item['height']
            peak.point = GeoPoint.objects.create(
                latitude=GeoPoint.degree_from_string(item['point']['lat']),
                longitude=GeoPoint.degree_from_string(item['point']['lon']),
            )
            peak.save()

        return 'Initial data is updated'
