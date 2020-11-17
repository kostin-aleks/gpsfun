import re
from django.db import models

from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.GeoMap.models import Location


class GeoKret(models.Model):
    name = models.CharField(max_length=128)
    location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    gkid = models.IntegerField(default=0)
    waypoint = models.CharField(max_length=32, null=True)
    type_code = models.CharField(max_length=2)
    name = models.CharField(max_length=128, blank=True, null=True)
    distance = models.IntegerField(default=0)
    owner_id = models.IntegerField(null=True)
    state = models.IntegerField(null=True)
    image = models.CharField(max_length=64, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    admin_code = models.CharField(max_length=6, blank=True, null=True)


    class Meta:
        db_table = u'geokret'

    def __unicode__(self):
        return u'%s/%s/%s' % (self.id, self.gkid, self.name.decode('utf-8'))

    @property
    def latitude_degree(self):
        return self.location.NS_degree

    @property
    def longitude_degree(self):
        return self.location.EW_degree

    @property
    def latitude_degree_minutes(self):
        d = (None,None)
        if self.location and self.location.NS_degree is not None:
            d = point_degree_minutes(self.location.NS_degree)

        return d

    @property
    def longitude_degree_minutes(self):
        d = (None,None)
        if self.location and self.location.EW_degree is not None:
            d = point_degree_minutes(self.location.EW_degree)

        return d

    @property
    def site(self):
        return 'geokrety.org'

    @property
    def url(self):
        return 'http://geokrety.org/konkret.php?id=%s' % self.gkid

    @property
    def reference_number(self):
        return 'GK%X' % (self.gkid or 0)

    @property
    def html_refnum(self):
        refnum = '%-7s' % self.reference_number
        refnum = refnum.replace(' ','&nbsp;')
        return refnum

    @property
    def html_distance(self):
        distance = '%6s' % self.distance
        distance = distance.replace(' ','&nbsp;')
        return distance

    @property
    def waypoint_url(self):
        wp = self.waypoint.upper()
        t = re.compile('\w{1,2}[\dA-F]+')
        if not t.match(wp):
            wp = ''
        if wp[:2] in ('TR', 'MS', 'MV', 'VI', 'LT', 'LV'):
            wp = wp[:2] + '/' + wp[2:]
        return 'http://geokrety.org/go2geo/index.php?wpt=%s' % wp

