#!/usr/bin/env python
"""
NAME
     map_update_shukach_caches.py

DESCRIPTION
     Updates list of caches from shukach.com
"""

import json
import re
from datetime import datetime
import requests

from django.core.management.base import BaseCommand

from gpsfun.main.models import log
from gpsfun.main.db_utils import sql2val
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import (Geothing, Geosite, BlockNeedBeDivided)
from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.utils import (
    update_geothing, create_new_geothing, TheGeothing, TheLocation)


OPENSITES = {

    'OCNL': {
        'MY_CONSUMER_KEY': '6kCMkHVLXGpyZKBmqqHm',
        'RECTANGLES': [
            (-90, 0, 0, 180),
            (-90, -180, 0, 0),
            (0, 0, 45, 90),

            (45, 0, 50, 25),

            (50, 0, 51, 3),
            (50, 3, 51, 5),

            (50, 5, 51, 6),
            (50, 6, 51, 7),

            (51, 0, 52, 3),

            (51, 3, 51.5, 4),
            (51.5, 3, 52, 4),
            (51, 4, 51.5, 5),

            (51.5, 4, 52, 4.5),
            (51.5, 4.5, 52, 5),

            (51, 5, 51.5, 6),

            (51.5, 5, 52, 5.5),
            (51.5, 5.5, 52, 6),

            (51, 6, 51.25, 6.25),
            (51.25, 6, 51.5, 6.25),

            (51, 6.25, 51.5, 6.5),

            (51, 6.5, 51.5, 7),

            (51.5, 6, 51.75, 6.5),

            (51.75, 6, 52, 6.25),
            (51.75, 6.25, 52, 6.5),

            (51.5, 6.5, 51.75, 7),
            (51.75, 6.5, 52, 7),

            (50, 7, 51, 15),
            (51, 7, 52, 15),

            (52, 0, 53.5, 3),

            (52, 3, 52.5, 4),
            (52.5, 3, 53.5, 4),
            (52, 4, 52.5, 5),
            (52.5, 4, 53.5, 5),

            (52, 5, 52.5, 6),
            (52.5, 5, 53.5, 6),
            (52, 6, 52.5, 7),

            (52.5, 6, 53.5, 6.5),
            (52.5, 6.5, 53.5, 7),

            (53.5, 0, 55, 7),

            (52, 7, 52.75, 7.5),
            (52.75, 7, 53.5, 7.5),
            (52, 7.5, 53.5, 8),

            (52, 8, 53.5, 9),

            (52, 9, 53.5, 11),
            (52, 11, 53.5, 15),

            (53.5, 7, 55, 15),

            (50, 15, 52, 25),
            (52, 15, 55, 25),

            (45, 25, 50, 45),
            (50, 25, 55, 45),

            (55, 0, 90, 45),
            (45, 45, 55, 90),
            (55, 45, 90, 90),

            (0, 90, 45, 180),
            (45, 90, 90, 180),
            (0, -180, 90, 0),
        ],
        'FIELDS': 'code|name|location|type|status|url|owner|date_created',
        'url_pattern': 'http://opencaching.nl/okapi/services/caches/shortcuts/search_and_retrieve?consumer_key=%s&search_method=services/caches/search/bbox&search_params={"bbox":"%s","limit":"500"}&retr_method=services/caches/geocaches&retr_params={"fields":"%s"}&wrap=true',
        'log_key': 'map_ocnl_caches',
        'code_re': r'OB([\dA-F]+)$',
    },

    'OCUK': {
        'MY_CONSUMER_KEY': 'AxFqHPRKSmSxLvqSrsFV',
        'RECTANGLES': [
            (-90, 0, 0, 180),
            (-90, -180, 0, 0),
            (0, -180, 60, -120),
            (60, -180, 90, -120),
            (0, -120, 30, -60),
            (30, -120, 45, -90),
            (30, -90, 38, -60),
            (38, -90, 45, -75),
            (38, -75, 45, -60),
            (45, -120, 60, -90),
            (45, -90, 60, -60),
            (60, -120, 90, -60),
            (0, -60, 30, 0),
            (30, -60, 45, -30),
            (30, -30, 45, 0),
            (45, -60, 60, -30),
            (45, -30, 53, -15),
            (45, -15, 49, -7),
            (45, -7, 49, 0),
            (49, -15, 53, -7),
            (49, -7, 51, 0),
            (51, -7, 53, 0),
            (53, -30, 60, -15),
            (53, -15, 60, 0),
            (60, -60, 90, 0),
            (0, 0, 30, 60),
            (30, 0, 45, 60),
            (45, 0, 52, 15),
            (52, 0, 60, 15),
            (45, 15, 52, 30),
            (52, 15, 60, 30),
            (45, 30, 60, 60),
            (60, 0, 90, 60),
            (0, 60, 30, 120),
            (30, 60, 90, 120),
            (0, 120, 30, 180),
            (30, 120, 90, 180),
        ],
        'FIELDS': 'code|name|location|type|status|url|owner|date_created',
        'url_pattern': 'http://opencaching.org.uk/okapi/services/caches/shortcuts/search_and_retrieve?consumer_key=%s&search_method=services/caches/search/bbox&search_params={"bbox":"%s","limit":"500"}&retr_method=services/caches/geocaches&retr_params={"fields":"%s"}&wrap=true',
        'log_key': 'map_ocuk_caches',
        'code_re': r'OK([\dA-F]+)$',
    },

    'OCPL': {
        'MY_CONSUMER_KEY': 'fky3LF9xvWz9y7Gs3tZ6',
        'RECTANGLES': [
            (-90, 0, 0, 180),
            (-90, -180, 0, 0),
            (0, 0, 45, 90),
            (0, 90, 45, 180),
            (45, 0, 51, 12),
            (51, 0, 57, 12),
            (45, 12, 48, 19),
            (48, 12, 49.5, 15),
            (49.5, 12, 51, 15),
            (48, 15, 49.5, 19),
            (49.5, 15, 51, 15.5),
            (49.5, 15.5, 49.75, 16),
            (49.75, 15.5, 51, 15.75),
            (49.75, 15.75, 51, 16),
            (49.5, 16, 51, 16.5),
            (49.5, 16.5, 51, 17),
            (49.5, 17, 51, 17.5),
            (49.5, 17.5, 51, 18),
            (49.5, 18, 50.2, 18.5),
            (50.2, 18, 50.6, 18.5),
            (50.6, 18, 51, 18.5),
            (49.5, 18.5, 49.8, 19),
            (49.8, 18.5, 50.2, 19),
            (50.2, 18.5, 50.6, 18.75),
            (50.2, 18.75, 50.4, 18.85),
            (50.2, 18.85, 50.3, 19),
            (50.3, 18.85, 50.4, 19),
            (50.4, 18.75, 50.6, 19),
            (50.6, 18.5, 51, 19),
            (45, 19, 48, 25),
            (48, 19, 49.5, 20.5),
            (48, 20.5, 49.5, 22),
            (49.5, 19, 50.0, 19.35),
            (50.0, 19, 50.2, 19.35),
            (49.5, 19.35, 50.2, 19.75),
            (50.2, 19, 50.3, 19.35),
            (50.3, 19, 50.4, 19.35),
            (50.2, 19.35, 50.4, 19.75),
            (50.4, 19, 50.6, 19.4),
            (50.4, 19.4, 50.6, 19.75),
            (50.6, 19, 50.8, 19.35),
            (50.8, 19, 51, 19.35),
            (50.6, 19.35, 51, 19.75),
            (49.5, 19.75, 49.8, 20.5),
            (49.8, 19.75, 50.2, 20.05),
            (49.8, 20.05, 50.2, 20.5),
            (50.2, 19.75, 50.6, 20.5),
            (50.6, 19.75, 50.8, 20.5),
            (50.8, 19.75, 51, 20.5),
            (49.5, 20.5, 50.2, 21.2),
            (50.2, 20.5, 50.6, 21.2),
            (50.6, 20.5, 50.8, 21.2),
            (50.8, 20.5, 51, 20.65),
            (50.8, 20.65, 51, 20.8),
            (50.8, 20.8, 51, 21.2),
            (49.5, 21.2, 50.2, 22),
            (50.2, 21.2, 51, 22),
            (48, 22, 49.5, 25),
            (49.5, 22, 49.75, 22.5),
            (49.75, 22, 51, 22.3),
            (49.75, 22.3, 51, 22.5),
            (49.5, 22.5, 49.75, 23.0),
            (49.75, 22.5, 51, 22.75),
            (49.75, 22.75, 51, 23.0),
            (49.5, 23, 49.75, 23.25),
            (49.75, 23, 49.85, 23.25),
            (49.85, 23, 50.3, 23.25),
            (50.3, 23, 50.6, 23.25),
            (50.6, 23, 51, 23.25),
            (49.5, 23.25, 50.5, 23.5),
            (50.5, 23.25, 51, 23.5),
            (49.5, 23.5, 51, 24.0),
            (49.5, 24.0, 51, 24.4),
            (49.5, 24.4, 51, 25),
            (51, 12, 53, 13.5),
            (51, 13.5, 52, 15),
            (52, 13.5, 52.5, 15),
            (52.5, 13.5, 53, 15),
            (53, 12, 54, 13.5),
            (53, 13.5, 53.5, 14.2),
            (53, 14.2, 53.25, 14.6),
            (53.25, 14.2, 53.5, 14.3),
            (53.25, 14.3, 53.5, 14.45),
            (53.25, 14.45, 53.4, 14.6),
            (53.4, 14.45, 53.45, 14.52),
            (53.4, 14.52, 53.45, 14.6),
            (53.45, 14.45, 53.5, 14.6),
            (53, 14.6, 53.5, 15),
            (53.5, 13.5, 54, 14.25),
            (53.5, 14.25, 53.75, 14.55),
            (53.75, 14.25, 54, 14.55),
            (53.5, 14.55, 54, 15),
            (51, 15, 52, 15.5),
            (51, 15.5, 51.5, 16),
            (51.5, 15.5, 51.75, 15.75),
            (51.75, 15.5, 52, 15.75),
            (51.5, 15.75, 52, 16),
            (52, 15, 53, 15.5),
            (52, 15.5, 53, 16),
            (51, 16, 51.5, 16.5),
            (51.5, 16, 52, 16.5),
            (51, 16.5, 51.5, 16.7),
            (51, 16.7, 51.25, 16.85),
            (51, 16.85, 51.25, 17),
            (51.25, 16.7, 51.5, 17),
            (51.5, 16.5, 52, 17),
            (52, 16, 52.5, 16.5),
            (52, 16.5, 52.5, 16.7),
            (52, 16.7, 52.25, 17),
            (52.25, 16.7, 52.5, 16.85),
            (52.25, 16.85, 52.4, 17),
            (52.4, 16.85, 52.5, 17),
            (52.5, 16, 53, 17),
            (51, 17, 51.15, 17.15),
            (51, 17.15, 51.15, 17.25),
            (51.15, 17, 51.25, 17.25),
            (51, 17.25, 51.25, 17.5),
            (51.25, 17, 51.5, 17.5),
            (51.5, 17, 52, 17.5),
            (51, 17.5, 52, 18),
            (52, 17, 52.5, 17.5),
            (52.5, 17, 53, 17.5),
            (52, 17.5, 53, 18),
            (51, 18, 52, 19),
            (52, 18, 53, 19),
            (53, 15, 54, 15.5),
            (53, 15.5, 54, 16),
            (53, 16, 54, 16.5),
            (53, 16.5, 54, 17),
            (53, 17, 54, 17.5),
            (53, 17.5, 53.5, 18),
            (53.5, 17.5, 54, 18),
            (53, 17.5, 53.5, 18),
            (53.5, 18, 53.5, 18.5),
            (53.5, 18, 54, 18.5),
            (53, 18.5, 53.5, 19),
            (53.5, 18.5, 53.75, 19),
            (53.75, 18.5, 54, 19),
            (54, 12, 56, 15),
            (56, 12, 57, 15),
            (54, 15, 55, 16),
            (54, 16, 54.15, 16.25),
            (54.15, 16, 54.25, 16.25),
            (54.25, 16, 54.5, 16.25),
            (54, 16.25, 54.5, 16.5),
            (54.5, 16, 55, 16.5),
            (54, 16.5, 55, 17),
            (55, 15, 56, 17),
            (54, 17, 54.5, 17.25),
            (54, 17.25, 54.25, 17.5),
            (54.25, 17.25, 54.5, 17.5),
            (54, 17.5, 54.5, 18),
            (54.5, 17, 55, 17.5),
            (54.5, 17.5, 55, 18),
            (54, 18, 54.5, 18.5),
            (54.5, 18, 55, 18.25),
            (54.5, 18.25, 55, 18.5),
            (54, 18.5, 54.25, 18.75),
            (54.25, 18.5, 54.35, 18.65),
            (54.35, 18.5, 54.4, 18.65),
            (54.4, 18.5, 54.5, 18.65),
            (54.25, 18.65, 54.5, 18.75),
            (54, 18.75, 54.5, 19),
            (54.5, 18.5, 55, 19),
            (55, 17, 56, 19),
            (56, 15, 57, 19),
            (51, 19, 51.5, 19.75),
            (51.5, 19, 52, 19.35),
            (51.5, 19.35, 51.75, 19.75),
            (51.75, 19.35, 52, 19.55),
            (51.75, 19.55, 52, 19.75),
            (51, 19.75, 52, 20.5),
            (52, 19, 52.25, 20.5),
            (52.25, 19, 52.5, 20.5),
            (52.5, 19, 53, 20.5),
            (51, 20.5, 51.5, 21.2),
            (51, 21.2, 51.5, 22),
            (51.5, 20.5, 52, 22),
            (52, 20.5, 52.2, 20.85),
            (52.2, 20.5, 52.35, 20.85),
            (52.35, 20.5, 52.5, 20.85),
            (52, 20.85, 52.12, 21.2),
            (52.12, 20.85, 52.25, 21),
            (52.12, 21, 52.18, 21.2),
            (52.18, 21, 52.25, 21.2),
            (52.25, 20.85, 52.35, 21.2),
            (52.35, 20.85, 52.5, 21.2),
            (52.5, 20.5, 53, 21.2),
            (52, 21.2, 52.5, 22),
            (52.5, 21.2, 53, 22),
            (53, 19, 53.5, 20.5),
            (53.5, 19, 54, 20.5),
            (53, 20.5, 54, 22),
            (51, 22, 51.25, 22.75),
            (51, 22.75, 51.25, 23.15),
            (51, 23.15, 51.25, 23.5),
            (51.25, 22, 51.5, 23.5),
            (51.5, 22, 52, 23.5),
            (52, 22, 52.5, 23.5),
            (52.5, 22, 53, 23.5),
            (51, 23.5, 53, 25),
            (53, 22, 53.5, 23.0),
            (53, 23, 53.5, 23.25),
            (53, 23.25, 53.5, 23.5),
            (53.5, 22, 54, 23.5),
            (53, 23.5, 54, 25),
            (54, 19, 55.5, 20.5),
            (54, 20.5, 55.5, 22),
            (55.5, 19, 57, 22),
            (54, 22, 57, 25),
            (57, 0, 70, 25),
            (45, 25, 57, 45),
            (57, 25, 70, 45),
            (70, 0, 90, 45),
            (45, 45, 70, 90),
            (70, 45, 90, 90),
            (45, 90, 90, 180),
            (0, -180, 90, 0),
        ],
        'FIELDS': 'code|name|location|type|status|url|owner|date_created',
        'url_pattern': 'http://opencaching.pl/okapi/services/caches/shortcuts/search_and_retrieve?consumer_key=%s&search_method=services/caches/search/bbox&search_params={"bbox":"%s","limit":"500"}&retr_method=services/caches/geocaches&retr_params={"fields":"%s"}&wrap=true',
        'log_key': 'map_ocpl_caches',
        'code_re': r'OP([\dA-F]+)$',
    },
}

OCPL_TYPES = {
    'Virtual': 'VI',
    'Traditional': 'TR',
    'Multi': 'MS',
    'Quiz': 'QZ',
    'Other': 'OT',
    'Moving': 'MO',
    'Event': 'EV',
    'Webcam': 'WC',
    }


def process(rectangle, geosite, params, run_index):
    """ process """
    bbox = [str(x) for x in rectangle]
    url = params.get('url_pattern') % (
        params['MY_CONSUMER_KEY'],
        '|'.join(bbox),
        params['FIELDS'])

    try:
        with requests.Session() as session:
            data = session.get(url).content
    except Exception as exception:
        print('exception', exception)
        return

    caches_data = json.loads(data)
    caches = caches_data.get('results')
    count = len(caches or [])

    more_data = caches_data.get('more')
    if more_data or count > 450:
        BlockNeedBeDivided.objects.create(
            geosite=geosite,
            bb='|'.join(bbox),
            idx=run_index,
            added=datetime.now())

    if not count:
        return

    counter = 0
    ucounter = 0
    ncounter = 0

    for code, cache in caches.items():
        counter += 1
        the_geothing = TheGeothing()
        the_location = TheLocation()
        locations = cache.get('location').split('|')
        lat_degree = float(locations[0])
        the_location.ns_degree = lat_degree
        lon_degree = float(locations[1])
        the_location.ew_degree = lon_degree
        the_geothing.code = cache.get('code')
        the_geothing.name = cache.get('name')

        if cache.get('status') != 'Available':
            continue

        the_geothing.type_code = OCPL_TYPES.get(cache.get('type'))
        cache_url = cache.get('url')
        if not cache_url:
            continue
        preg = re.compile(params['code_re'])
        dgs = preg.findall(cache_url)
        if not dgs:
            continue
        the_geothing.pid = int(dgs[0], 16)
        if cache.get('owner'):
            owner_name = cache.get('owner').get('username')
        the_geothing.author = owner_name
        date_created = cache.get('date_created')
        if date_created:
            date_created = date_created[:10]
            parts = date_created.split('-')
            if parts and len(parts) == 3:
                dtime = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                the_geothing.created_date = dtime

        if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
            geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)

            if geothing is not None:
                ucounter += update_geothing(geothing, the_geothing, the_location) or 0
            else:
                create_new_geothing(the_geothing, the_location, geosite)
                ncounter += 1

    message = f'OK. updated {ucounter}, new {ncounter}'
    log(params.get('log_key'), message)


class Command(BaseCommand):
    """ command """
    help = 'Updates list of caches from shukach.com'

    def handle(self, *args, **options):
        run_index = BlockNeedBeDivided.next_index()
        for key, value in OPENSITES.items():
            print('OPENSITE', key)
            geosite = Geosite.objects.get(code=key)
            for rec in value.get('RECTANGLES'):
                process(rec, geosite, value, run_index)

            log(value.get('log_key'), 'OK')

        blocks = BlockNeedBeDivided.objects.filter(
            idx=run_index).order_by('geosite__id')
        if blocks:
            print('Too big blocks')
            for block in blocks:
                print(block.geosite.code, block.geosite.id, block.bb)

        sql = """
            select COUNT(*)
            FROM
            (
            select g.code as code, count(id) as cnt
            from geothing g
            group by g.code
            having cnt > 1
            ) as tbl
            """
        dcount = sql2val(sql)
        message = f'doubles {dcount}'
        log('map_opencaching', message)
        print(message)

        return 'List of caches from opencaching has updated'
