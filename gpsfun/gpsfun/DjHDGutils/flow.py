"""
flow
"""
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch


def view_to_url(view_name, *args, **kwargs):
    try:
        return reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        try:
            project_name = settings.SETTINGS_MODULE.split('.')[0]
            return reverse(project_name + '.' + view_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            return ''
