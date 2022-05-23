"""
views for application geoname
"""

from django.utils import translation

from gpsfun.main.db_utils import get_object_or_none
from gpsfun.main.ajax import accept_ajax
from gpsfun.main.GeoName.models import (
    GeoCountry, GeoCountryAdminSubject,
    GeoCity, country_by_code, region_by_code, get_city_by_geoname)


@accept_ajax
def get_country_regions(request):
    """ get country regions """
    result = {'status': 'ERR'}

    country_code = request.GET.get('country')

    if not country_code:
        return result
    country = get_object_or_none(GeoCountry, iso=country_code)
    address = 'Ukraine, Kharkov'
    if country:
        address = f'{country.name},{country.capital}'

    regions = GeoCountryAdminSubject.objects.filter(country_iso=country_code)
    regions = regions.exclude(name='').exclude(name__isnull=True)
    regions = regions.values('code', 'name').order_by('name')
    regions = list(regions)

    result['regions'] = sorted(regions, key=lambda x: x['name'])
    result['address'] = address
    result['status'] = 'OK'

    return result


@accept_ajax
def get_region_cities(request):
    """ get region cities """
    result = {'status': 'ERR'}

    country_code = request.GET.get('country')
    region_code = request.GET.get('region')
    if not (country_code and region_code):
        return result

    country = get_object_or_none(GeoCountry, iso=country_code)
    region = get_object_or_none(
        GeoCountryAdminSubject,
        code=region_code,
        country_iso=country_code)
    address = 'Ukraine, Kharkov'
    if country is not None and region is not None:
        address = f'{country.name},{region.name}'

    cities = GeoCity.objects.filter(country=country_code)
    cities = cities.filter(admin1=region_code)
    cities = cities.exclude(name='').exclude(name__isnull=True)
    cities = cities.order_by('name')
    cities = [{
        'code': city.geonameid,
        'name': city.localized_name(translation.get_language())}
        for city in cities]

    result['cities'] = sorted(cities, key=lambda x: x['name'])
    result['address'] = address
    result['status'] = 'OK'

    return result


@accept_ajax
def get_waypoint_address(request):
    """ get waypoint address """
    result = {'status': 'ERR'}
    country_code = request.GET.get('country')
    region_code = request.GET.get('region')
    city_code = request.GET.get('city')
    if not country_code or country_code == 'NONE':
        return result

    result['status'] = 'OK'
    country = country_by_code(country_code)
    if not region_code or region_code == 'NONE':
        result['address'] = country or ''
        return result

    region = region_by_code(country_code, [region_code])
    if not city_code or city_code == 'NONE':
        result['address'] = f"{country or ''} {region or ''}"
        return result

    city = get_city_by_geoname(city_code)
    if city:
        result['address'] = city.address_string()
        return result
    result['address'] = f"{country or ''} {region or ''}"

    return result
