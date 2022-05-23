"""
GPS FUN admin models
"""

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class AdministratorPreferences(models.Model):
    """
    Administrator Preferences
    """
    user = models.ForeignKey(
        get_user_model(), unique=True, null=True, blank=True, on_delete=models.CASCADE)
    skin = models.FilePathField(
        path=settings.SITE_ROOT + 'htdocs/gpsfun-admin/', match=r'skin.*\.css')
    rows_per_page = models.IntegerField(default=15)

    class Meta:
        db_table = 'adminprefs'
