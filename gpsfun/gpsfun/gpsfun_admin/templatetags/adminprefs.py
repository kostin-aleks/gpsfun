from django import template
from django.urls import reverse
from gpsfun.gpsfun_admin.models import AdministratorPreferences

register = template.Library()

@register.simple_tag
def admin_skin(user):
    prefs = None
    if user and not user.is_anonymous:
        prefs = user.administratorpreferences_set.all()
    if not prefs:
        prefs = AdministratorPreferences.objects.filter(user=None)
    return prefs[0].skin.split('/')[-1]
