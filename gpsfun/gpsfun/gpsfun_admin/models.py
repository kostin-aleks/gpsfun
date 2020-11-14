from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class AdministratorPreferences(models.Model):
    user = models.ForeignKey(
        User, unique=True, null=True, blank=True, on_delete=models.CASCADE)
    skin = models.FilePathField(
        path=settings.SITE_ROOT + 'htdocs/gpsfun-admin/', match='skin.*\.css')
    rows_per_page = models.IntegerField(default=15)

    class Meta:
        db_table = 'adminprefs'

