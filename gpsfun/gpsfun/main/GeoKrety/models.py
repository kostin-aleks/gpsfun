"""
GeoKrety models
"""
import re
from django.db import models

from gpsfun.main.GeoMap.models import Location, point_degree_minutes


class GeoKret(models.Model):
    """ GeoKret """
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

    def __str__(self):
        name = self.name.decode('utf-8')
        return f'{self.id}/{self.gkid}/{name}'

    @property
    def latitude_degree(self):
        """ latitude degree """
        return self.location.ns_degree

    @property
    def longitude_degree(self):
        """ longitude degree """
        return self.location.ew_degree

    @property
    def latitude_degree_minutes(self):
        """ latitude degree and minutes """
        degree = (None, None)
        if self.location and self.location.ns_degree is not None:
            degree = point_degree_minutes(self.location.ns_degree)

        return degree

    @property
    def longitude_degree_minutes(self):
        """ longitude degree and minutes """
        degree = (None, None)
        if self.location and self.location.ew_degree is not None:
            degree = point_degree_minutes(self.location.ew_degree)

        return degree

    @property
    def site(self):
        """ geokret site """
        return 'geokrety.org'

    @property
    def url(self):
        """ url to geokret """
        return f'http://geokrety.org/konkret.php?id={self.gkid}'

    @property
    def reference_number(self):
        """ reference number of geokret """
        gkid = self.gkid or 0
        return f'GK{gkid:X}'

    @property
    def html_refnum(self):
        """ reference number of geokret """
        refnum = f'{self.reference_number:07s}'
        refnum = refnum.replace(' ', '&nbsp;')
        return refnum

    @property
    def html_distance(self):
        """ distance """
        distance = f'{self.distance:6s}'
        distance = distance.replace(' ', '&nbsp;')
        return distance

    @property
    def waypoint_url(self):
        """ url to geokret waypoint """
        wpoint = self.waypoint.upper()
        treg = re.compile(r'\w{1,2}[\dA-F]+')
        if not treg.match(wpoint):
            wpoint = ''
        if wpoint[:2] in ('TR', 'MS', 'MV', 'VI', 'LT', 'LV'):
            wpoint = wpoint[:2] + '/' + wpoint[2:]
        return f'http://geokrety.org/go2geo/index.php?wpt={wpoint}'
