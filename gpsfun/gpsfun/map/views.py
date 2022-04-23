"""
views for application map
"""

from time import time
import re

from django.shortcuts import render
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.ajax import accept_ajax
from gpsfun.main.db_utils import iter_sql

from gpsfun.main.GeoMap.models import (CACHE_TYPES, CACHE_KINDS,
    GEOCACHING_ONMAP_TYPES)
from gpsfun.main.GeoMap.models import Geothing
from gpsfun.main.utils import MAX_POINTS
from gpsfun.main.utils import points_rectangle
from gpsfun.main.Utils.unicode_urlify.urlify import urlify


def geocaching_su_cach_url(pid):
    """ cache url """
    return f"http://www.geocaching.su/?pn=101&cid={pid}"


def geocaching_su_geocacher_url(pid):
    """ geocacher url """
    return f"http://www.geocaching.su/profile.php?pid={pid}"


def translated_country(country):
    """ translated country name """
    country['country_name'] = _(country['country_name'])
    return country


def map_center(mapbounds):
    """ center of map """
    return [(mapbounds.get('bottom') + mapbounds.get('top')) / 2.0,
            (mapbounds.get('left') + mapbounds.get('right')) / 2.0]


def caches_map(request):
    """ return map of caches """
    default_mapbounds = {
        'bottom': 49.5,
        'top': 50.5,
        'left': 36.2,
        'right': 36.6,
    }

    user_types = request.session.get('map_type', ['REAL', 'MULTISTEP'])
    mapbounds = request.session.get('mapbounds') or default_mapbounds
    maps_center = request.session.get('center') or {'lat': 50.0, 'lon': 36.4}
    map_zoom = request.session.get('zoom') or 14

    type_ids = request.session.get('map_type') or ['REAL', 'MULTISTEP']
    cache_types = CACHE_KINDS
    result = get_points(mapbounds, type_ids)
    print(result.get('caches'))
    return render(
        request,
        'Map/geocaching_map.3.html',
        {
            'caches': result.get('caches'),
            'caches_count': len(result.get('caches')),
            'cache_types': cache_types,
            'cache_types_len': len(cache_types) + 1,
            'user_types': user_types,
            'map_rect': result.get('mapbounds'),
            'max_points': MAX_POINTS,
            'map_center': maps_center,
            'map_zoom': map_zoom,
        })


@accept_ajax
def map_cache_info(request):
    """ return information for cache """
    result = {'status': 'ERR'}
    pid = request.GET.get('cache_pid')
    site_code = request.GET.get('cache_site')
    cache = get_object_or_none(Geothing, pid=pid, geosite__code=site_code)
    if not cache:
        return result

    result['content'] = render(
        request,
        'Map/cache_info.html',
        {'cache': cache, })
    result['status'] = 'OK'

    return result


def get_points(mapbounds, type_ids):
    """ get points """
    caches = Geothing.objects.filter(
            location__NS_degree__gt=mapbounds['bottom'],
            location__NS_degree__lt=mapbounds['top'],
            location__EW_degree__gt=mapbounds['left'],
            location__EW_degree__lt=mapbounds['right'],
            type_code__in=GEOCACHING_ONMAP_TYPES)

    type_list = types_by_kind(type_ids)
    caches = caches.filter(type_code__in=type_list)
    caches_count = caches.count()

    cache_list = []
    if caches_count < MAX_POINTS:
        for cache in caches:
            if len(cache_list) < MAX_POINTS:
                cache_list.append(
                    {
                        'pid': cache.pid,
                        'name': cache.name,
                        'site': cache.site,
                        'type_code': cache.type_code,
                        'site_code': cache.geosite.code,
                        'content': render_to_string(
                            'Map/cache_info.html',
                            {'cache': cache}),
                        'latitude_degree': cache.latitude_degree,
                        'longitude_degree': cache.longitude_degree
                    })

    points_list = []

    return {
        'points': points_list,
        'caches': cache_list,
        'count': caches_count,
        'status': 'OK'
    }


@accept_ajax
def map_rectangle_things(request):
    """ return things for map rectangle """
    result = {'status': 'ERR'}

    mapbounds = {
        'top': float(request.GET.get('top') or 50.5),
        'left': float(request.GET.get('left') or 36.2),
        'bottom': float(request.GET.get('bottom') or 49.5),
        'right': float(request.GET.get('right') or 36.6),
    }
    center = {
        'lon': float(request.GET.get('center_lon') or 36.4),
        'lat': float(request.GET.get('center_lat') or 50.0),
    }
    request.session['mapbounds'] = mapbounds
    request.session['center'] = center
    request.session['zoom'] = int(request.GET.get('zoom') or 14)

    type_ids = request.session.get('map_type') or ['REAL', 'MULTISTEP']

    result = get_points(mapbounds, type_ids)

    return result


@accept_ajax
def map_show_types(request):
    """ return map types """
    result = {'status': 'OK'}
    type_ids = request.GET.getlist('type[]')
    request.session['map_type'] = type_ids

    return result


@accept_ajax
def map_search_waypoint(request):
    """ search map waypoint """
    result = {'status': 'ERR'}

    waypoint = request.GET.get('waypoint')
    request.session['map_waypoint'] = waypoint

    if waypoint is None:
        return result

    caches = []
    if waypoint:
        caches = waypoints_by_mask(waypoint)

    result['caches'] = get_cache_list(caches)
    result['rect'] = points_rectangle(caches)
    result['status'] = 'OK'

    return result


def waypoints_by_mask(waypoint):
    """ return waypoints by mask """
    sql = waypoint_mask_sql(waypoint)
    return get_caches_list(sql)


def get_cache(cache):
    """ return the cache """
    return {
        'pid': cache.pid,
        'name': cache.name,
        'site': cache.site,
        'type_code': cache.type_code,
        'site_code': cache.geosite.code,
        'content': render_to_string(
            'Map/cache_info.html',
            {'cache': cache}),
        'latitude_degree': cache.latitude_degree,
        'longitude_degree': cache.longitude_degree
    }


def get_cache_list(caches):
    """ get list of caches """
    return [get_cache(cache) for cache in caches]


def get_caches_list(sql):
    """ get list of caches by sql query """
    caches = []
    if not sql:
        return []
    for row in iter_sql(sql):
        cache = Geothing.objects.get(pk=row[0])
        caches.append(cache)
    return caches


def all_caches_sql():
    """ sql query to get caches """
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


def waypoint_mask_sql(waypoint):
    """ return sql query to get waypoints by mask"""
    if not waypoint:
        return all_caches_sql()

    sql = None
    wpoint = waypoint.strip().upper()
    pwp = re.compile('(OP|TR|MS|GC|OC|OX|GR|GL|OK|GA|OZ|TR|RH|OU|TC|OS|ON|OL|OJ|N|GE|WM|SH|TP|TB|OB)[\d,A-F]*') #OB GL
    if pwp.match(wpoint):
        sql = waypont_sql(wpoint)

    if sql is None:
        if not waypoint:
            return all_caches_sql()
        sql = cache_name_sql(waypoint)

    return sql


def cache_name_sql(name):
    """ return sql query to get cache by name """
    return f"""
        select
            gt.id
        from geothing gt
        left join location l on gt.location_id=l.id
        left join geosite gsite on gt.geosite_id=gsite.id
        where gt.name RLIKE '.*{name.encode('utf8')}.*' and
              l.id is not null
        """


def waypont_sql(waypoint):
    """ return sql query to get geothing by waypoint """
    return f"""
        select
            gt.id
        from geothing gt
        left join location l on gt.location_id=l.id
        left join geosite gsite on gt.geosite_id=gsite.id
        where gt.code RLIKE '^{waypoint}.*' and
              l.id is not null
        """


def selected_caches(request):
    """ get selected caches """
    caches = []
    user_country = request.session.get('map_country')
    user_region = request.session.get('map_region')
    user_types = request.session.get('map_type')
    user_sites = request.session.get('site')

    if user_country and user_region:
        caches = Geothing.objects.filter(
            country_code=user_country,
            type_code__in=GEOCACHING_ONMAP_TYPES
        )
        caches = caches.select_related('location', 'geosite')
        if not 'all' in user_sites:
            caches = caches.filter(geosite__code__in=user_sites)
        if not 'all' in user_region:
            caches = caches.filter(admin_code__in=user_region)
        if user_types:
            if not 'all' in user_types:
                type_list = types_by_kind(user_types)
                caches = caches.filter(type_code__in=type_list)
        else:
            caches = []
    return caches


def wpt_file(caches):
    """ get wpt file with caches """
    response_text = render_to_string('caches.wpt', {'caches': caches})
    response = HttpResponse(response_text)
    response['Content-Type'] = 'text'
    response['Content-Disposition'] = f'attachment; filename = geocaches_{int(time())}.wpt'
    response['Content-Length'] = str(len(response_text))
    return response


def map_import_caches_wpt(request):
    """ view to get wpt file """
    caches = selected_caches(request)

    return wpt_file(caches)


def map_import_caches_wpt_translit(request):
    """ view to get wpt file with transliterated data """
    caches = selected_caches(request)
    for cache in caches:
        if cache.name:
            cache.name = slugify(urlify(cache.name))
        else:
            cache.name = 'noname'

    return wpt_file(caches)


def types_by_kind(type_ids):
    """ get types by kind """
    lst = []
    for type_ in CACHE_TYPES:
        if type_ in type_ids:
            for item in CACHE_TYPES[type_]:
                lst.append(item)
    return lst
