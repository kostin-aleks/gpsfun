"""
template tags custom admin
"""
from django.urls import reverse, NoReverseMatch
from django import template


register = template.Library()


@register.simple_tag
def url_to_edit_object(object):
    url = reverse(
        'admin:%s_%s_change' % (
            object._meta.app_label,
            object._meta.module_name),
        args=[object.id])
    return url
