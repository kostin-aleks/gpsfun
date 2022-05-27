"""
views related to application user
"""

from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from gpsfun.main.misc import atoi
from gpsfun.main.GeoName.models import get_city_by_geoname
from gpsfun.main.GeoMap.models import Location
from gpsfun.user.forms import CityForm
from gpsfun.geocaching_su_stat.views import get_degree


def user_profile(request):
    """ return user profile """
    return render(
        request,
        'User/profile.html',
        {})


def user_profile_edit(request):
    """ return page to edit user profile """

    def get_form_parameters(city):
        """ return form parameters for the city """
        data = (None, None, None)
        if city:
            data = (city.geonameid, city.admin1, city.country)
        return data

    user = request.user
    user_city = None
    city_id, region, country = get_form_parameters(user_city)
    if user and user.gpsfunuser.geocity:
        user_city = user.gpsfunuser.geocity
        city_id, region, country = get_form_parameters(user_city)

    if request.method == 'POST':
        if 'save' in request.POST:
            city_geoname = atoi(request.POST.get('city'))
            city = get_city_by_geoname(city_geoname)
            if city:
                if user.gpsfunuser.geocity != city:
                    user.gpsfunuser.geocity = city
                    user.gpsfunuser.save()
                    messages.success(request, _('Your city changed'))
                user_city = city
                city_id, region, country = get_form_parameters(user_city)
            else:
                if user_city:
                    user.gpsfunuser.geocity = None
                    user.gpsfunuser.save()
                    messages.warning(request, _('You reset city'))

            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.gpsfunuser.middle_name = request.POST.get('middle_name')
            user.gpsfunuser.gcsu_username = request.POST.get('nickname')
            user.gpsfunuser.save()
            user.save()

            messages.success(request, 'Profile details updated.')

    form = CityForm(
        initial={
            'country': country,
            'subject': region,
            'city': city_id,
        },
        user_city=user_city)

    return render(
        request,
        'User/profile_edit.html',
        {
            'form_city': form,
        })


def set_user_location(user, data):
    """ set user location """

    def is_valid_position(position):
        """ check coordinates """
        return bool(position.get('latitude') and position.get('longitude'))

    user_changed = False
    position = {
        'latitude': None,
        'longitude': None,
    }
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    lat_sign = data.get('lat_sign')
    lon_sign = data.get('lon_sign')

    degree = get_degree(latitude)
    if degree is not None:
        position['latitude'] = -degree if lat_sign == 'S' else degree
    degree = get_degree(longitude)
    if degree is not None:
        position['longitude'] = -degree if lon_sign == 'W' else degree

    if is_valid_position(position):
        if user.gpsfunuser.location is None:
            location = Location.objects.create(
                NS_degree=position.get('latitude'),
                EW_degree=position.get('longitude'))
            user.gpsfunuser.location = location
            user_changed = True
        else:
            user.gpsfunuser.location.NS_degree = position.get('latitude')
            user.gpsfunuser.location.EW_degree = position.get('longitude')
            user.gpsfunuser.location.save()
            user_changed = True

    return user_changed
