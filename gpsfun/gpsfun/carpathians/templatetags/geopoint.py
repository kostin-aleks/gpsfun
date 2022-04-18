"""
Template tags and filters related to geopoint
"""

from django import template


register = template.Library()


DMS = 'dms'


def split_to_dms(coordinate):
    """
    Split coordinate DD.DDDDD into D M S
    """
    coordinate = abs(float(coordinate))
    degree = int(coordinate)
    float_minutes = (coordinate - degree) * 60.0
    minutes = int(float_minutes)
    seconds = int(round((float_minutes - minutes) * 60.0, 0))
    return degree, minutes, seconds


def format_coordinate(coordinate, fmt):
    """
    format coordinate string
    """
    if fmt == DMS:
        degree, minutes, seconds = split_to_dms(coordinate)
        return f"{degree:02}&deg; {minutes:02}&prime; {seconds:02}&Prime;"
    return str(coordinate)


@register.filter
def point(value, arg):
    """
    template filter
    format point coordinates string
    """
    north = 'с.ш.' if value.latitude >= 0 else 'ю.ш.'
    east = 'в.д.' if value.longitude >= 0 else 'з.д.'

    return f"{format_coordinate(value.latitude, arg)} {north} {format_coordinate(value.longitude, arg)} {east}"


@register.filter
def osmlink(value):
    """
    template filter
    link to openstreetmap
    """
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
