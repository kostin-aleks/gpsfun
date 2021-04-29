from django import template
from django.template import Variable


register = template.Library()


def split_to_dms(c):
    c = abs(float(c))
    degree = int(c)
    float_minutes = (c - degree) * 60.0
    minutes = int(float_minutes)
    seconds = int(round((float_minutes - minutes) * 60.0, 0))
    return degree, minutes, seconds


def format_coordinate(c, fmt):
    if fmt == 'dms':
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


