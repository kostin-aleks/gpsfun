"""
admin preferences for gps fun
"""

from django import template
from gpsfun.gpsfun_admin.models import AdministratorPreferences

register = template.Library()


@register.simple_tag
def admin_skin(user):
    """
    admin skin
    """
    prefs = None
    if user and not user.is_anonymous:
        prefs = user.administratorpreferences_set.all()
    if not prefs:
        prefs = AdministratorPreferences.objects.filter(user=None)
    return prefs[0].skin.split('/')[-1]
