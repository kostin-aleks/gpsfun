"""
template tags datetimetags
"""
from django import template


register = template.Library()


@register.simple_tag
def args(vars, var, a1, a2=None):
    vars = vars.copy()
    vars[var] = str(a1) + str(a2 or '')
    return vars.urlencode()
