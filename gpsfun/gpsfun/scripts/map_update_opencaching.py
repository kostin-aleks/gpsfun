#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection
from time import time
from datetime import datetime, date, timedelta
import re
from gpsfun.main.GeoMap.models import GEOCACHING_ONMAP_TYPES
from gpsfun.main.GeoMap.models import Geothing, Geosite, Location, \
     BlockNeedBeDivided
from gpsfun.main.models import log
from gpsfun.main.GeoName.models import GeoCountry
from gpsfun.main.db_utils import sql2list, sql2val

import sys
import os
import urllib2
import json
from gpsfun.main.db_utils import execute_query
from DjHDGutils.dbutils import get_object_or_none
from  gpsfun.main.utils import update_geothing, \
      create_new_geothing, TheGeothing, TheLocation

OPENSITES = {
    #'OCUS': {
        #'MY_CONSUMER_KEY': 'WwPNF3Z4qZhRsad6Uz4D',
        #'RECTANGLES': [
            #(-90, 0, 0, 180),
            #(-90, -180, 0, 0),
            #(0, 0, 90, 180),
            #(0, -180, 45, -90),
            #(45, -180, 90, -90),

            #(0, -90, 25, -45),

            #(25, -90, 35, -70),

            #(35, -90, 40, -80),
            #(40, -90, 45, -80),
            #(35, -80, 40, -70),
            #(40, -80, 45, -70),

            #(25, -70, 35, -45),
            #(35, -70, 45, -45),

            #(0, -45, 25, 0),
            #(25, -45, 45, 0),

            #(45, -90, 90, 0),
            #],
        #'FIELDS': 'code|name|location|type|status|url|owner|date_created',
        #'url_pattern': 'http://opencaching.us/okapi/services/caches/shortcuts/search_and_retrieve?consumer_key=%s&search_method=services/caches/search/bbox&search_params={"bbox":"%s","limit":"500"}&retr_method=services/caches/geocaches&retr_params={"fields":"%s"}&wrap=true',
        #'log_key': 'map_ocus_caches',
        #'code_re': 'OU([\dA-F]+)$',
    #},

    'OCNL': {
        'MY_CONSUMER_KEY': '6kCMkHVLXGpyZKBmqqHm',
        'RECTANGLES': [
            (-90, 0, 0, 180),
            (-90, -180, 0, 0),
            (0, 0, 45, 90),

            (45, 0, 50, 25),

            (50, 0, 51, 7),

            (51, 0, 52, 3),

            (51, 3, 51.5, 4),
            (51.5, 3, 52, 4),
            (51, 4, 51.5, 5),

            (51.5, 4, 52, 4.5),
            (51.5, 4.5, 52, 5),

            (51, 5, 51.5, 6),

            (51.5, 5, 52, 5.5),
            (51.5, 5.5, 52, 6),

            (51, 6, 51.5, 7),
            (51.5, 6, 52, 7),

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
            (52, 7, 53.5, 15),
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
        'code_re': 'OB([\dA-F]+)$',
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
        'code_re': 'OK([\dA-F]+)$',
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
                                                (49.5, 15, 51, 16),
                                                (49.5, 16, 51, 17),
                                                (49.5, 17, 51, 18),
                                                    (49.5, 18, 50.2, 18.5),
                                                    (50.2, 18, 51, 18.5),
                                                    (49.5, 18.5, 50.2, 19),
                                                    (50.2, 18.5, 50.6, 18.75),
                                                    (50.2, 18.75, 50.4, 19),
                                                    (50.4, 18.75, 50.6, 19),
                                                    (50.6, 18.5, 51, 19),
                                    (45, 19, 48, 25),
                                        (48, 19, 49.5, 22),
                                                (49.5, 19, 50.2, 19.75),
                                                (50.2, 19, 50.4, 19.75),
                                                (50.4, 19, 50.6, 19.75),
                                                (50.6, 19, 51, 19.75),
                                                (49.5, 19.75, 49.8, 20.5),
                                                (49.8, 19.75, 50.2, 20.5),
                                                (50.2, 19.75, 51, 20.5),
                                                (49.5, 20.5, 50.2, 21.2),
                                                (50.2, 20.5, 51, 21.2),
                                                (49.5, 21.2, 50.2, 22),
                                                (50.2, 21.2, 51, 22),
                                        (48, 22, 49.5, 25),
                                        (49.5, 22, 51, 25),
                                        (51, 12, 53, 15),
                                            (53, 12, 54, 13.5),
                                                (53, 13.5, 53.5, 14.2),
                                                (53, 14.2, 53.5, 14.6),
                                                (53, 14.6, 53.5, 15),
                                                (53.5, 13.5, 54, 15),
                                                (51, 15, 52, 16),
                                                (52, 15, 53, 16),
                                                (51, 16, 52, 17),
                                                (52, 16, 52.5, 17),
                                                (52.5, 16, 53, 17),
                                                (51, 17, 52, 18),
                                                (52, 17, 53, 18),
                                                (51, 18, 52, 19),
                                                (52, 18, 53, 19),
                                            (53, 15, 54, 17),
                                                (53, 17, 54, 18),
                                                    (53, 18, 53.5, 18.5),
                                                    (53.5, 18, 54, 18.5),
                                                    (53, 18.5, 53.5, 19),
                                                    (53.5, 18.5, 54, 19),
                                        (54, 12, 56, 15),
                                        (56, 12, 57, 15),
                                            (54, 15, 55, 17),
                                            (55, 15, 56, 17),
                                                (54, 17, 55, 18),
                                                    (54, 18, 54.5, 18.5),
                                                    (54.5, 18, 55, 18.5),
                                                    (54, 18.5, 54.5, 19),
                                                    (54.5, 18.5, 55, 19),
                                            (55, 17, 56, 19),
                                        (56, 15, 57, 19),
                                                (51, 19, 52, 19.75),
                                                (51, 19.75, 52, 20.5),
                                            (52, 19, 52.5, 20.5),
                                            (52.5, 19, 53, 20.5),
                                            (51, 20.5, 52, 22),
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
                                                (52, 21.2, 53, 22),
                                            (53, 19, 53.5, 20.5),
                                            (53.5, 19, 54, 20.5),
                                            (53, 20.5, 54, 22),
                                        (51, 22, 53, 25),
                                            (53, 22, 53.5, 23.5),
                                            (53.5, 22, 54, 23.5),
                                            (53, 23.5, 54, 25),
                                    (54, 19, 57, 25),
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
            'code_re': 'OP([\dA-F]+)$',
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


def process(rectangle, geosite, params):
    print(geosite)
    bbox = [str(x) for x in  rectangle]
    url = params.get('url_pattern') % (params['MY_CONSUMER_KEY'],
                                       '|'.join(bbox),
                                       params['FIELDS'])

    try:
        response = urllib2.urlopen(url)
        print('GOT')
    except Exception as e:
        print('exception', e)
        return
    data = response.read()
    caches_data = json.loads(data)
    caches = caches_data.get('results')

    more_data = caches_data.get('more')
    if more_data:
        BlockNeedBeDivided.objects.create(geosite=geosite,
                                          bb='|'.join(bbox),
                                          added=datetime.now())
    if not len(caches):
        return
    k = 0
    uc = 0
    nc = 0

    for code, cache in caches.iteritems():
        k += 1
        the_geothing = TheGeothing()
        the_location = TheLocation()
        locations = cache.get('location').split('|')
        lat_degree = float(locations[0])
        the_location.NS_degree = lat_degree
        lon_degree = float(locations[1])
        the_location.EW_degree = lon_degree
        the_geothing.code = cache.get('code')
        the_geothing.name = cache.get('name')

        if cache.get('status') != 'Available':
            continue

        the_geothing.type_code = OCPL_TYPES.get(cache.get('type'))
        cache_url = cache.get('url')
        if not cache_url:
            continue
        p = re.compile(params['code_re'])
        dgs = p.findall(cache_url)
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
                dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                the_geothing.created_date = dt

        if the_geothing.type_code in GEOCACHING_ONMAP_TYPES:
            geothing = get_object_or_none(Geothing, pid=the_geothing.pid, geosite=geosite)

            if geothing is not None:
                uc += update_geothing(geothing, the_geothing, the_location) or 0
            else:
                create_new_geothing(the_geothing, the_location, geosite)
                nc += 1
    message = 'OK. updated %s, new %s' % (uc, nc)
    log(params.get('log_key'), message)

def main():
    LOAD_CACHES = True

    start = time()
    for k, v in OPENSITES.items():
        print('OPENSITE', k)
        geosite = Geosite.objects.get(code=k)
        for rec in v.get('RECTANGLES'):
            process(rec, geosite, v)

        log(v.get('log_key'), 'OK')

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
    dc = sql2val(sql)
    message = 'doubles %s' % dc
    log('map_opencaching', message)

    elapsed = time() - start
    print("Elapsed time -->", elapsed)

if __name__ == '__main__':
    main()
