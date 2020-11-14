from django.db import models

from django.contrib.auth.models import User
from django.db.models import signals
from gpsfun.main.signals import create_custom_user
from django.utils.translation import ugettext_lazy as _
from gpsfun.main.GeoName.models import GeoCity
from gpsfun.main.GeoMap.models import Location
from gpsfun.main.GeoCachSU.models import Geocacher

signals.post_save.connect(create_custom_user, sender=User)


class GPSFunUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_('user'))
    geocity = models.ForeignKey(
        GeoCity, null=True, db_index=True, on_delete=models.CASCADE)
    # location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    gcsu_username = models.CharField(max_length=32, unique=True, null=True)

    class Meta:
        db_table = u'gpsfunuser'

    def __unicode__(self):
        return u'user %s: ' % (self.user.username)

    def address(self):
        return self.geocity.address_string() if self.geocity else ''

    @property
    def avatar_url(self):
        try:
            return self.avatar.url
        except:
            return defaults.PYBB_DEFAULT_AVATAR_URL

    def get_profile(self):
        return self

    @property
    def is_banned(self):
        return False

    @property
    def geocaching_su_nickname(self):
        return self.gcsu_username if self.gcsu_username else self.user.username

    @property
    def geocacher(self):
        geocacher = Geocacher.objects.filter(
            nickname=self.geocaching_su_nickname).first()

        return geocacher if geocacher else None

