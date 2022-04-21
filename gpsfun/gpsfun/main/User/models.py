"""
models for main.User
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from gpsfun.main.signals import create_custom_user
from gpsfun.main.GeoName.models import GeoCity
# from gpsfun.main.GeoMap.models import Location
from gpsfun.main.GeoCachSU.models import Geocacher

User = get_user_model()
signals.post_save.connect(create_custom_user, sender=User)


class GPSFunUser(models.Model):
    """ GPSFunUser """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_('user'))
    geocity = models.ForeignKey(
        GeoCity, null=True, db_index=True, on_delete=models.CASCADE)
    # location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    gcsu_username = models.CharField(max_length=32, unique=True, null=True)

    class Meta:
        db_table = 'gpsfunuser'

    def __str__(self):
        return f'user {self.user.username}: '

    def address(self):
        """ user address """
        return self.geocity.address_string() if self.geocity else ''

    def get_profile(self):
        """ get user profile """
        return self

    @property
    def is_banned(self):
        """ is user banned ? """
        return False

    @property
    def geocaching_su_nickname(self):
        """ geocaching.su nick for the user """
        return self.gcsu_username if self.gcsu_username else self.user.username

    @property
    def geocacher(self):
        """ get geocacher related to the user """
        geocacher = Geocacher.objects.filter(
            nickname=self.geocaching_su_nickname).first()

        return geocacher if geocacher else None
