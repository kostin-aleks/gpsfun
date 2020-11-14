from django import template
from django.template.defaultfilters import stringfilter
from os.path import basename

register = template.Library()


@register.filter
@stringfilter
def slicefirst(value, arg=None):
    if arg is None:
        arg = 100

    if len(value) <= int(arg):
        return value
    else:
        return value[:int(arg)] + '...'


@register.filter
@stringfilter
def maxwordlength(value, arg=50):
    arg = int(arg)
    words = value.split(' ')
    newwords = []
    for word in words:
        if len(word) > arg:
            word = word[:arg] + '...'
        newwords.append(word)
    return ' '.join(newwords)


@register.filter
@stringfilter
def filebasename(value, arg=None):
    if value:
        return basename(value)


@register.filter
@stringfilter
def string_to_list(value):
    """
    Split string by \n
    """
    return list(value.split('\n'))
