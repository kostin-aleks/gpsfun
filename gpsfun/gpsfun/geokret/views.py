"""
views for application geokret
"""

import re
from datetime import datetime
from lxml import etree

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _

from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.ajax import accept_ajax
from gpsfun.main.db_utils import sql2table
from gpsfun.main.GeoKrety.models import GeoKret
from gpsfun.main.GeoName.models import GeoCountry
from gpsfun.main.models import LogUpdate, log_api
from gpsfun.main.utils import points_rectangle
from gpsfun.main.utils import MAX_POINTS


GEOKRETY_ONMAP_STATES = [0, 3]
SEARCH_TOOLTIP = _("Geokret or waypoint")


class KretyWaypoint:
    """ Kret waypoint """
    waypoint = None
    latitude = None
    longitude = None
    count = 0
    distance = 0


def geokrety_map(request):
    """ get map with geokrety """
    krety = []

    default_mapbounds = {
        'bottom': 49.5,
        'top': 50.5,
        'left': 36.2,
        'right': 36.6,
    }

    def rectagle_center(rectangle):
        """ get center of the rectangle """
        return {
            'lat': (rectangle['bottom'] + rectangle['top']) / 2.0,
            'lng': (rectangle['left'] + rectangle['right']) / 2.0
        }

    map_zoom = request.session.get('geokrety_zoom') or 14

    user_waypoint = request.session.get('geokrety_map_waypoint', '')
    geokret_waypoint = request.session.get('geokret_waypoint')
    mapbounds = request.session.get('geokrety_mapbounds') or {default_mapbounds}
    map_center = request.session.get(
        'geokrety_center') or rectagle_center(default_mapbounds)
    krety = waypoints_rectangle(mapbounds)

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
            'tooltip_text': SEARCH_TOOLTIP,
            'user_waypoint': user_waypoint,
            'max_points': MAX_POINTS,
            'map_center': map_center,
            'map_zoom': map_zoom,
            'geokret_waypoint': geokret_waypoint,
        })


@accept_ajax
def map_geokret_info(request):
    """ get map information """
    result = {'status': 'ERR'}
    waypoint = request.GET.get('waypoint')
    krety = GeoKret.objects.filter(
        waypoint=waypoint,
        state__in=GEOKRETY_ONMAP_STATES)
    krety = krety.order_by('name')
    waypoint_url = url_by_waypoint(waypoint)
    result['content'] = render(
        request,
        'Map/geokret_info.html',
        {
            'geokrety': krety,
            'waypoint': {
                'code': waypoint,
                'url_to': waypoint_url}
        })
    result['status'] = 'OK'

    return result


@accept_ajax
def geokrety_map_get_geokrety(request):
    """ get list of geokrety """
    result = {'status': 'ERR'}

    mapbounds = {
        'top': float(request.GET.get('top') or 0),
        'left': float(request.GET.get('left') or 0),
        'bottom': float(request.GET.get('bottom') or 0),
        'right': float(request.GET.get('right') or 0),
    }

    request.session['geokrety_mapbounds'] = mapbounds
    request.session['geokrety_zoom'] = request.GET.get('zoom') or 14
    request.session['geokrety_center'] = {
        'lat': request.GET.get('center_lat'),
        'lng': request.GET.get('center_lng'), }
    # user_waypoint = request.session.get('geokrety_map_waypoint', '')
    krety = waypoints_rectangle(mapbounds)

    result['krety'] = get_kret_list(krety)
    result['rect'] = points_rectangle(krety)
    result['count'] = len(krety)
    result['status'] = 'OK'

    return result


@accept_ajax
def geokrety_map_change_country(request):
    """ change country """
    result = {'status': 'ERR'}
    country_code = request.GET.get('country')
    request.session['geokrety_map_country'] = country_code

    if not country_code:
        return result

    if country_code != 'SEARCH':
        request.session['geokrety_map_waypoint'] = None

    country = get_object_or_none(GeoCountry, iso=country_code)

    address = 'Ukraine, Kharkov'
    if country:
        address = f'{country.name},{country.capital}'

    krety = waypoints_with_geokrety(country_code)

    result['krety'] = get_kret_list(krety)
    result['rect'] = points_rectangle(krety)
    result['address'] = address
    result['status'] = 'OK'

    return result


@accept_ajax
def geokrety_map_search_waypoint(request):
    """ search waypoint """
    result = {'status': 'ERR'}

    waypoint = request.GET.get('waypoint')
    request.session['geokrety_map_waypoint'] = waypoint

    if waypoint is None:
        return result

    found_kret = None
    krety = []

    if waypoint:
        krety = waypoints_by_mask(waypoint)[:1]
        if krety:
            found_kret = {
                'lat': krety[0].latitude,
                'lng': krety[0].longitude}
            request.session['geokret_waypoint'] = found_kret

            # krety_list = get_kret_list(krety)
            rect = points_rectangle(krety)

            mapbounds = {
                'top': rect['lat_max'],
                'left': rect['lng_min'],
                'bottom': rect['lat_min'],
                'right': rect['lng_max'],
            }
            krety = waypoints_rectangle(mapbounds)
    if not krety:
        mapbounds = request.session.get('geokrety_mapbounds')
        krety = waypoints_with_geokrety_rectangle(mapbounds)

    result['krety'] = get_kret_list(krety)
    result['rect'] = points_rectangle(krety)
    result['kret_waypoint'] = found_kret
    result['status'] = 'OK'

    return result


def waypoints_with_geokrety(user_country):
    """ get list of waypoints """
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
    """ get list of waypoints for the rectangle """
    sql = get_rectangle_sql(mapbounds)
    return get_krety_list(sql)


def url_by_waypoint(waypoint):
    """ get url for waypoint """
    wpoint = ''
    su_t = re.compile(r'TR|MS\d+')
    if waypoint and len(waypoint) > 3:
        wpoint = waypoint.upper()
        treg = re.compile(r'\w{1,2}[\dA-F]+')
        if not treg.match(wpoint):
            wpoint = ''
    if wpoint and wpoint.startswith('OB'):
        return f'http://www.opencaching.nl/viewcache.php?wp={wpoint}'

    if su_t.match(wpoint):
        wpoint = f'{wpoint[:2]}/{wpoint[2:]}'

    return f'http://geokrety.org/go2geo/{wpoint}'


def geokrety_api_who_in_cache(request, cache_code):
    """ get geokrety in cache """
    root_tree = etree.Element('waypoint')
    root_tree.attrib['code'] = cache_code
    desc_tree = etree.SubElement(root_tree, 'description')
    desc_tree.text = 'Krety in Cache Listing Generated from gps-fun.info'
    url_tree = etree.SubElement(root_tree, 'url')
    url_tree.text = f'http://geokrety.org/szukaj.php?wpt={cache_code}'
    time_tree = etree.SubElement(root_tree, 'time')
    time_tree.text = datetime.now().isoformat()
    geokrety_tree = etree.SubElement(root_tree, 'geokrety')
    geokrety = GeoKret.objects.filter(
        state__in=GEOKRETY_ONMAP_STATES,
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

    response_text = f'<?xml version="1.0" encoding="utf-8"?>{etree.tostring(root_tree).decode("utf-8")}'
    response = HttpResponse(response_text)
    response['Content-Type'] = 'text/xml'
    response['Content-Length'] = str(len(response_text))

    try:
        log_api('whoincache', request.META.get('REMOTE_ADDR', ''))
    except:
        pass

    return response


def waypoints_rectangle(mapbounds):
    """ get list of waypoints for map bounds """
    sql = all_krety_sql()
    if len(mapbounds.keys()):
        sql += f"""
        HAVING l.ns_degree > {mapbounds['bottom']}
            and l.ns_degree < {mapbounds['top']}
            and l.ew_degree > {mapbounds['left']}
            and l.ew_degree < {mapbounds['right']}
        """

    sql += f" LIMIT {MAX_POINTS + 1}"

    krety = get_krety_list(sql)

    return krety


def waypoint_mask_sql(waypoint):
    """ get sql query to get waypoints by the mask """
    if not waypoint:
        return all_krety_sql()

    sql = None
    wpoint = waypoint.strip().upper()
    pwp = re.compile(
        r'(OP|TR|MS|GC|OC|OX|GR|GL|OK|GA|OZ|TR|RH|OU|TC|OS|ON|OL|OJ|N|GE|WM|SH|TP|TB|OB)[\d,A-F]*')  # OB GL
    pgk = re.compile(r'GK([\d,A-F]+)')
    if pwp.match(wpoint) and len(wpoint) < 9:
        return waypont_sql(wpoint)

    if pgk.match(wpoint):
        hexcode = pgk.findall(wpoint)
        if hexcode and len(hexcode):
            hexcode = hexcode[0]
            try:
                kret_id = int(hexcode, 16)
            except:
                kret_id = 0
            return geokret_sql(kret_id)

    if not waypoint:
        return all_krety_sql()
    sql = kret_name_sql(waypoint)
    return sql


def waypoints_by_mask(waypoint):
    """ get list of waypoints by the mask """
    sql = waypoint_mask_sql(waypoint)
    return get_krety_list(sql)


def get_kret(kret_point):
    """ get geokret """
    krety = GeoKret.objects.filter(
        waypoint=kret_point.waypoint, state__in=(0, 3)).exclude(
            location__isnull=True)
    waypoint_url = krety[0].waypoint_url if krety.count() else ''

    return {
        'waypoint': kret_point.waypoint,
        'name': kret_point.waypoint,
        'distance': kret_point.distance or 0,
        'content': render_to_string(
            'Map/geokret_info.html',
            {
                'kret_point': kret_point,
                'krety': krety,
                'waypoint_url': waypoint_url}),
        'latitude': kret_point.latitude,
        'longitude': kret_point.longitude}


def get_kret_list(krety):
    """ get list of geokrety """
    return [get_kret(kret) for kret in krety]


def get_rectangle_sql(mapbounds):
    """ get sql query to get geokrety for map bounds """
    return f"""
        select
           kret.waypoint,
           l.ns_degree as latitude,
           l.ew_degree as longitude,
           COUNT(kret.id) as cnt,
           MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
            and l.ns_degree > {mapbounds['bottom']}
            and l.ns_degree < {mapbounds['top']}
            and l.ew_degree > {mapbounds['left']}
            and l.ew_degree < {mapbounds['right']}
        group by kret.waypoint, l.ns_degree, l.ew_degree
        """


def all_krety_sql():
    """ sql query to get all geokrety """
    return """
        select
           kret.waypoint,
           l.ns_degree,
           l.ew_degree,
           COUNT(kret.id) as cnt,
           MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.ns_degree, l.ew_degree
        """


def get_country_sql(user_country):
    """ sql query to get geokrety for the country """
    return f"""
        select
           kret.waypoint,
           l.ns_degree,
           l.ew_degree,
           COUNT(kret.id) as cnt,
           MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.country_code='{user_country}' and
            kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.ns_degree, l.ew_degree
        """


def get_all_countries_sql():
    """ get sql query to get geokrety for all countries """
    return """
        select
            kret.waypoint,
            l.ns_degree,
            l.ew_degree,
            COUNT(kret.id) as cnt,
            MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where
            kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.ns_degree, l.ew_degree
        """


def get_no_country_sql():
    """ get geokrety that is not linked to any country """
    return """
        select
            kret.waypoint,
            l.ns_degree,
            l.ew_degree,
            COUNT(kret.id) as cnt,
            MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.country_code IS NULL and
            kret.state in (0,3) and kret.waypoint is not null
            and length(kret.waypoint) > 0 and l.id is not null
        group by kret.waypoint, l.ns_degree, l.ew_degree
        """


def waypont_sql(waypoint):
    """ get geokrety for the waypoint by mask """
    return f"""
        select
            kret.waypoint,
            l.ns_degree,
            l.ew_degree,
            COUNT(kret.id) as cnt,
            MAX(kret.distance) as distance
        from geokret kret
        left join location l on kret.location_id=l.id
        where kret.waypoint is not null and length(kret.waypoint) > 0
            and kret.waypoint RLIKE '^{waypoint}.*' and
            kret.state in (0,3)
            and l.id is not null
        group by kret.waypoint, l.ns_degree, l.ew_degree
        """


def geokret_sql(kret_id):
    """ query to get geokret by id """
    return f"""
            select
                kret.waypoint,
                l.ns_degree,
                l.ew_degree,
                COUNT(kret.id) as cnt,
                MAX(kret.distance) as distance
            from geokret kret
            left join location l on kret.location_id=l.id
            where kret.waypoint is not null and length(kret.waypoint) > 0
                and kret.gkid = {kret_id} and
                kret.state in (0,3)
                and l.id is not null
            group by kret.waypoint, l.ns_degree, l.ew_degree
            """


def kret_name_sql(name):
    """ query to get geokret by name """
    name = name.replace(' ', '%')
    return f"""
            select
                kret.waypoint,
                l.ns_degree,
                l.ew_degree,
                COUNT(kret.id) as cnt,
                MAX(kret.distance) as distance
            from geokret kret
            left join location l on kret.location_id=l.id
            where kret.waypoint is not null and length(kret.waypoint) > 0
                and kret.name LIKE '%{name}%' and
                kret.state in (0,3)
                and l.id is not null
            group by kret.waypoint, l.ns_degree, l.ew_degree
            """


def get_krety_list(sql):
    """ get krety using sql query """
    krety = []
    if not sql:
        return krety
    for row in sql2table(sql):
        kret = KretyWaypoint()
        kret.waypoint = row[0]
        kret.count = row[3]
        kret.latitude = row[1]
        kret.longitude = row[2]
        kret.distance = row[4]
        krety.append(kret)
    return krety
