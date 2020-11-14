# coding: utf-8

from django.utils import translation

from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.DjHDGutils.ajax import accept_ajax
from gpsfun.main.GeoName.models import (GeoCountry, GeoCountryAdminSubject,
     GeoCity, country_by_code, region_by_code, get_city_by_geoname)


@accept_ajax
def get_country_regions(request):
    rc = {'status': 'ERR',
          }

    country_code = request.GET.get('country')

    if not country_code:
        return rc
    country = get_object_or_none(GeoCountry, iso=country_code)
    address = 'Ukraine, Kharkov'
    if country:
        address = '%s,%s' % (country.name, country.capital)

    regions = GeoCountryAdminSubject.objects.filter(country_iso=country_code)
    regions = regions.exclude(name='').exclude(name__isnull=True)
    regions = regions.values('code', 'name').order_by('name')
    regions = list(regions)

    rc['regions'] = sorted(regions, key=lambda x: x['name'])
    rc['address'] = address
    rc['status'] = 'OK'

    return rc


@accept_ajax
def get_region_cities(request):
    rc = {'status': 'ERR',
          }

    country_code = request.GET.get('country')
    region_code = request.GET.get('region')
    if not (country_code and region_code):
        return rc

    country = get_object_or_none(GeoCountry, iso=country_code)
    region = get_object_or_none(GeoCountryAdminSubject,
                                code=region_code,
                                country_iso=country_code)
    address = 'Ukraine, Kharkov'
    if country is not None and region is not None:
        address = '%s,%s' % (country.name, region.name)

    cities = GeoCity.objects.filter(country=country_code)
    cities = cities.filter(admin1=region_code)
    cities = cities.exclude(name='').exclude(name__isnull=True)
    cities = cities.order_by('name')
    cities = [{'code': city.geonameid,
               'name': city.localized_name(translation.get_language())} \
              for city in cities]

    rc['cities'] = sorted(cities, key=lambda x: x['name'])
    rc['address'] = address
    rc['status'] = 'OK'

    return rc


@accept_ajax
def get_waypoint_address(request):
    rc = {'status': 'ERR',
          }
    country_code = request.GET.get('country')
    region_code = request.GET.get('region')
    city_code = request.GET.get('city')
    if not country_code or country_code == 'NONE':
        return rc

    rc['status'] = 'OK'
    country = country_by_code(country_code)
    if not region_code or region_code == 'NONE':
        rc['address'] = country or ''
        return rc

    region = region_by_code(country_code, [region_code])
    if not city_code or city_code == 'NONE':
        rc['address'] = '%s %s' % (country or '',
                                   region or '')
        return rc

    city = get_city_by_geoname(city_code)
    if city:
        rc['address'] = city.address_string()
        return rc
    else:
        rc['address'] = '%s %s' % (country or '',
                                   region or '')
        return rc

    return rc
