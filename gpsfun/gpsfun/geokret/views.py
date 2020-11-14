# coding: utf-8
import re
from datetime import datetime
from lxml import etree
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max
from gpsfun.DjHDGutils.dbutils import iter_sql
from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.DjHDGutils.ajax import accept_ajax

from gpsfun.main.GeoKrety.models import GeoKret
from gpsfun.main.GeoName.models import GeoCountry
from gpsfun.main.models import LogUpdate, log_api
from gpsfun.main.utils import points_rectangle

GEOKRETY_ONMAP_STATES = [0, 3]
search_tooltip = _("Find the waypoint")


class KretyWaypoint:
    waypoint = None
    latitude = None
    longitude = None
    count = 0
    distance = 0


def geokrety_map(request):
    krety = []

    user_waypoint = request.session.get('geokrety_map_waypoint', '')
    mapbounds = request.session.get('geokrety_mapbounds') or {}
    krety = waypoints_rectangle_with_mask(user_waypoint, mapbounds)

    update_date = LogUpdate.objects.filter(update_type='kret')\
        .aggregate(last_date=Max('update_date'))

    return render(
        request,
        'Map/geokrety_map.html',
        {
            'geokrety': krety,
            'geokrety_count': len(krety),
            'map_rect': points_rectangle(krety),
            'update_date': update_date.get("last_date"),
            'tooltip_text': search_tooltip,
            'user_waypoint': user_waypoint
        })


@accept_ajax
def map_geokret_info(request):
    rc = {'status': 'ERR',
          }
    waypoint = request.GET.get('waypoint')
    krety = GeoKret.objects.filter(
        waypoint=waypoint,
        state__in=GEOKRETY_ONMAP_STATES)
    krety = krety.order_by('name')
    waypoint_url = url_by_waypoint(waypoint)
    rc['content'] = render(
        request,
        'Map/geokret_info.html',
        {
            'geokrety': krety,
            'waypoint': {
                'code': waypoint,
                'url_to': waypoint_url}
        })
    rc['status'] = 'OK'

    return rc


@accept_ajax
def geokrety_map_get_geokrety(request):
    rc = {'status': 'ERR',
          }

    mapbounds = {
        'top': float(request.GET.get('top') or 0),
        'left': float(request.GET.get('left') or 0),
        'bottom': float(request.GET.get('bottom') or 0),
        'right': float(request.GET.get('right') or 0),
    }
    request.session['geokrety_mapbounds'] = mapbounds
    user_waypoint = request.session.get('geokrety_map_waypoint', '')
    krety = waypoints_rectangle_with_mask(user_waypoint, mapbounds)

    rc['krety'] = get_kret_list(krety)
    rc['rect'] = points_rectangle(krety)
    rc['status'] = 'OK'

    return rc


@accept_ajax
def geokrety_map_change_country(request):
    rc = {'status': 'ERR',
          }
    country_code = request.GET.get('country')
    request.session['geokrety_map_country'] = country_code

    if not country_code:
        return rc

    if country_code != 'SEARCH':
        request.session['geokrety_map_waypoint'] = None

    country = get_object_or_none(GeoCountry, iso=country_code)

    address = 'Ukraine, Kharkov'
    if country:
        address = '%s,%s' % (country.name, country.capital)

    krety = waypoints_with_geokrety(country_code)

    rc['krety'] = get_kret_list(krety)
    rc['rect'] = points_rectangle(krety)
    rc['address'] = address
    rc['status'] = 'OK'

    return rc


@accept_ajax
def geokrety_map_search_waypoint(request):
    rc = {'status': 'ERR',
          }

    waypoint = request.GET.get('waypoint')
    request.session['geokrety_map_waypoint'] = waypoint

    if waypoint is None:
        return rc

    if waypoint:
        krety = waypoints_by_mask(waypoint)
    else:
        mapbounds = request.session.get('geokrety_mapbounds')
        krety = waypoints_with_geokrety_rectangle(mapbounds)

    rc['krety'] = get_kret_list(krety)
    rc['rect'] = points_rectangle(krety)
    rc['status'] = 'OK'

    return rc


def waypoints_with_geokrety(user_country):
    sql = None
    if user_country == 'SEARCH':
        return []
    if user_country and len(user_country) == 2:
        sql = get_country_sql(user_country)
    if user_country and user_country == 'ALL':
        sql = get_all_countries_sql()
    if user_country and user_country == 'NONE':
        sql = get_no_country_sql()

    return get_krety_list(sql)


def waypoints_with_geokrety_rectangle(mapbounds):
    sql = get_rectangle_sql(mapbounds)
    return get_krety_list(sql)


def url_by_waypoint(waypoint):
    wp = ''
    su_t = re.compile('TR|MS\d+')
    if waypoint and len(waypoint) > 3:
        wp = waypoint.upper()
        t = re.compile('\w{1,2}[\dA-F]+')
        if not t.match(wp):
            wp = ''
    if wp and len(wp) and wp.startswith('OB'):
        return 'http://www.opencaching.nl/viewcache.php?wp=%s' % wp

    if su_t.match(wp):
        wp = '%s/%s' % (wp[:2], wp[2:])

    return 'http://geokrety.org/go2geo/%s' % wp


def geokrety_api_who_in_cache(request, cache_code):

    root_tree = etree.Element('waypoint')
    root_tree.attrib['code'] = cache_code
    desc_tree = etree.SubElement(root_tree, 'description')
    desc_tree.text = 'Krety in Cache Listing Generated from gps-fun.info'
    url_tree = etree.SubElement(root_tree, 'url')
    url_tree.text = 'http://geokrety.org/szukaj.php?wpt=%s' % cache_code
    time_tree = etree.SubElement(root_tree, 'time')
    time_tree.text = datetime.now().isoformat()
    geokrety_tree = etree.SubElement(root_tree, 'geokrety')
    geokrety = GeoKret.objects.filter(state__in=GEOKRETY_ONMAP_STATES,
                                      waypoint=cache_code)
    for geokret in geokrety:
        geokret_tree = etree.SubElement(geokrety_tree, 'geokret')
        id_tree = etree.SubElement(geokret_tree, 'id')
        id_tree.text = str(geokret.gkid)
        refnum_tree = etree.SubElement(geokret_tree, 'refnum')
        refnum_tree.text = geokret.reference_number
        name_tree = etree.SubElement(geokret_tree, 'name')
        name_tree.text = geokret.name
        distance_tree = etree.SubElement(geokret_tree, 'distance')
        distance_tree.text = str(geokret.distance)
        kret_url_tree = etree.SubElement(geokret_tree, 'kret_url')
        kret_url_tree.text = geokret.url

    response_text = '%s%s' % ('<?xml version="1.0" encoding="utf-8"?>',
                              etree.tostring(root_tree).decode("utf-8"))
    response = HttpResponse(response_text)
    response['Content-Type'] = u'text/xml'
    response['Content-Length'] = unicode(len(response_text))

    try:
        log_api('whoincache', request.META.get('REMOTE_ADDR', ''))
    except:
        pass

    return response


def waypoints_rectangle_with_mask(waypoint, mapbounds):
    sql = waypoint_mask_sql(waypoint)
    if len(mapbounds.keys()):
        sql += """
        HAVING l.NS_degree > {}
            and l.NS_degree < {}
            and l.EW_degree > {}
            and l.EW_degree < {}
        """.format(mapbounds['bottom'],
                   mapbounds['top'],
                   mapbounds['left'],
                   mapbounds['right'])

    return get_krety_list(sql)


def waypoint_mask_sql(waypoint):
    if not waypoint:
        return all_krety_sql()

    sql = None
    wpoint = waypoint.strip().upper()
    pwp = re.compile('(OP|TR|MS|GC|OC|OX|GR|GL|OK|GA|OZ|TR|RH|OU|TC|OS|ON|OL|OJ|N|GE|WM|SH|TP|TB|OB)[\d,A-F]*') #OB GL
    pgk = re.compile('GK([\d,A-F]+)')
    if pwp.match(wpoint):
        sql = waypont_sql(wpoint)

    if pgk.match(wpoint):
        hexcode = pgk.findall(wpoint)
        if hexcode and len(hexcode):
            hexcode = hexcode[0]
            try:
                kret_id = int(hexcode, 16)
            except:
                kret_id = 0
            sql = geokret_sql(kret_id)

    if sql is None:
        if not waypoint:
            return all_krety_sql()
        else:
            sql = kret_name_sql(waypoint)
    return sql


def waypoints_by_mask(waypoint):
    sql = waypoint_mask_sql(waypoint)
    return get_krety_list(sql)


def get_kret(kret):
    return {'waypoint': kret.waypoint,
            'name': kret.waypoint,
            'distance': kret.distance or 0,
            'latitude': kret.latitude,
            'longitude': kret.longitude}


def get_kret_list(krety):
    return [get_kret(kret) for kret in krety]


def get_rectangle_sql(mapbounds):
    return """
        select
           kret.waypoint,
           l.NS_degree,
           l.EW_degree,
           COUNT(kret.id) as cnt,
           MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
            and l.NS_degree > {}
            and l.NS_degree < {}
            and l.EW_degree > {}
            and l.EW_degree < {}
        group by kret.waypoint, l.NS_degree, l.EW_degree
        """.format(
                mapbounds['bottom'], mapbounds['top'],
                mapbounds['left'], mapbounds['right'])


def all_krety_sql():
    return """
        select
           kret.waypoint,
           l.NS_degree,
           l.EW_degree,
           COUNT(kret.id) as cnt,
           MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.NS_degree, l.EW_degree
        """


def get_country_sql(user_country):
    return """
        select
           kret.waypoint,
           l.NS_degree,
           l.EW_degree,
           COUNT(kret.id) as cnt,
           MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.country_code='{}' and
            kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.NS_degree, l.EW_degree
        """.format(user_country)


def get_all_countries_sql():
    return """
        select
            kret.waypoint,
            l.NS_degree,
            l.EW_degree,
            COUNT(kret.id) as cnt,
            MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where
            kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.NS_degree, l.EW_degree
        """


def get_no_country_sql():
    return """
        select
            kret.waypoint,
            l.NS_degree,
            l.EW_degree,
            COUNT(kret.id) as cnt,
            MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.country_code IS NULL and
            kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.NS_degree, l.EW_degree
        """


def waypont_sql(waypoint):
    return """
        select
            kret.waypoint,
            l.NS_degree,
            l.EW_degree,
            COUNT(kret.id) as cnt,
            MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.waypoint is not null and length(kret.waypoint) > 0
            and kret.waypoint RLIKE '^{}.*' and
            kret.state in (0,3)
            and l.id is not null
        group by kret.waypoint, l.NS_degree, l.EW_degree
        """.format(waypoint)


def geokret_sql(kret_id):
    return """
            select
                kret.waypoint,
                l.NS_degree,
                l.EW_degree,
                COUNT(kret.id) as cnt,
                MAX(kret.distance) as distance
            from geokret kret
            left join location l on kret.location_id=l.id
            where kret.waypoint is not null and length(kret.waypoint) > 0
                and kret.gkid = {} and
                kret.state in (0,3)
                and l.id is not null
            group by kret.waypoint, l.NS_degree, l.EW_degree
            """.format(kret_id)


def kret_name_sql(name):
    return """
            select
                kret.waypoint,
                l.NS_degree,
                l.EW_degree,
                COUNT(kret.id) as cnt,
                MAX(kret.distance) as distance
            from geokret kret
            left join location l on kret.location_id=l.id
            where kret.waypoint is not null and length(kret.waypoint) > 0
                and kret.name RLIKE '.*{}.*' and
                kret.state in (0,3)
                and l.id is not null
            group by kret.waypoint, l.NS_degree, l.EW_degree
            """.format(name.encode('utf8'))


def get_krety_list(sql):
    krety = []
    if not sql:
        return krety
    for row in iter_sql(sql):
        kret = KretyWaypoint()
        kret.waypoint = row[0]
        kret.count = row[3]
        kret.latitude = row[1]
        kret.longitude = row[2]
        kret.distance = row[4]
        krety.append(kret)
    return krety
