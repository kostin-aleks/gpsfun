import urllib
from django import template
from django.template import Variable


register = template.Library()


DMS = 'dms'


def split_to_dms(c):
    c = abs(float(c))
    degree = int(c)
    float_minutes = (c - degree) * 60.0
    minutes = int(float_minutes)
    seconds = int(round((float_minutes - minutes) * 60.0, 0))
    return degree, minutes, seconds


def format_coordinate(c, fmt):
    if fmt == DMS:
        degree, minutes, seconds = split_to_dms(c)
        return "{:02d}&deg; {:02d}&prime; {:02d}&Prime;".format(
            degree, minutes, seconds)
    return str(c)


@register.filter
def point(value, arg):
    north = 'с.ш.' if value.latitude >= 0 else 'ю.ш.'
    east = 'в.д.' if value.longitude >= 0 else 'з.д.'

    return "{} {} {} {}".format(
        format_coordinate(value.latitude, arg), north,
        format_coordinate(value.longitude, arg), east,
    )


@register.filter
def osmlink(value):
    north = 'N' if value.latitude >= 0 else 'S'
    east = 'E' if value.longitude >= 0 else 'W'
    osm_link = "https://www.openstreetmap.org/search?query="
    query_string = "{}{} {}{}#map=15/{}/{}"
    osm_link = osm_link + query_string.format(
        north, format_coordinate(value.latitude, DMS),
        east, format_coordinate(value.longitude, DMS),
        value.latitude, value.longitude
    )
    return osm_link
