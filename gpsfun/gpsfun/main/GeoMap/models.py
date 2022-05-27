"""
GeoMap models
"""
import random
from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.db.models import Max

GEOCACHING_CACHE_TYPES = {
    # geocaching.su
    'MS': _('Trad Multi step'),
    'MV': _('Virtual Multi step'),
    'TR': _('Traditional'),
    'VI': _('Virtual'),
    # shukach.com
    'Q': _('Quest'),
    'P': _('Place of interest'),
    'H': _('Cache'),
    'T': _('Treasure'),
    'C': _('Casket'),
    'Con': _('Crossing'),
    'G': _('Geodesy'),
    # opencaching.pl
    'QZ': _('Quiz'),
    'OT': _('Other'),
    'MO': _('Moving'),
    'WC': _('Webcam'),
}

CACHE_TYPES = {
    'REAL': ('TR', 'H', 'T', 'C', 'OT', 'MO', 'DR'),
    'VIRTUAL': ('VI', 'P', 'Con', 'WC'),
    'MULTISTEP': ('MS', 'QZ', 'MT'),
    'MULTISTEPVIRTUAL': ('MV', 'Q',),
}

CACHE_KINDS = (
    {'code': 'REAL', 'name': _('Traditional')},
    {'code': 'VIRTUAL', 'name': _('Virtual')},
    {'code': 'MULTISTEP', 'name': _('Multistep')},
    {'code': 'MULTISTEPVIRTUAL', 'name': _('Virtual Multistep')},
)

GEOCACHING_ONMAP_TYPES = ('MV', 'MS', 'TR', 'VI', 'Q', 'H', 'T', 'P',
                          'C', 'Con', 'QZ', 'MO', 'OT', 'WC', 'MT', 'DR')

NOISE = {
    'GC_SU': 500,
    'SHUKACH': 500,
}


def random_noise(noise):
    """ random value """
    return random.randrange(0, noise) / 1000000.0


class Location(models.Model):
    """ Location """
    ns_degree = models.FloatField(blank=True, null=True)
    ew_degree = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'location'

    def __str__(self):
        return f'location {self.id}: {self.ns_degree} / {self.ew_degree}'


class Geosite(models.Model):
    """ Geosite """
    code = models.CharField(max_length=16)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128, blank=True, null=True)
    cache_url = models.CharField(max_length=128, blank=True, null=True)
    url_by_code = models.BooleanField(default=False)
    enabled = models.BooleanField()
    logo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'geosite'

    def __str__(self):
        return f'Geosite {self.code}-{self.name}-{self.url}'

    def url2cache(self, pid, code):
        """ url to geocache """
        if self.url_by_code:
            return self.cache_url % code
        return self.cache_url % pid


class Geothing(models.Model):
    """ Geothing """
    geosite = models.ForeignKey(Geosite, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    pid = models.IntegerField(default=0)
    code = models.CharField(max_length=32)
    type_code = models.CharField(max_length=2)
    name = models.CharField(max_length=128, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    author = models.CharField(max_length=128, blank=True, null=True)
    cach_type = models.CharField(max_length=128, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    admin_code = models.CharField(max_length=6, blank=True, null=True)
    country_name = models.CharField(max_length=64, blank=True, null=True)
    oblast_name = models.CharField(max_length=128, blank=True, null=True)
    oblast = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'geothing'

    def __str__(self):
        return '{self.id}/{self.geosite.code}/{self.code}/{self.name}'

    @property
    def latitude_degree(self):
        """ latitude degree """
        return self.location.ns_degree + random_noise(NOISE.get(self.geosite.code) or 1)

    @property
    def longitude_degree(self):
        """ longitude degree """
        return self.location.ew_degree + random_noise(NOISE.get(self.geosite.code) or 1)

    @property
    def latitude_degree_minutes(self):
        """ latitude degree minutes """
        degree = (None, None)
        if self.location and self.location.ns_degree is not None:
            degree = point_degree_minutes(self.location.ns_degree)

        return degree

    @property
    def longitude_degree_minutes(self):
        """ longitude degree minutes """
        degree = (None, None)
        if self.location and self.location.EW_degree is not None:
            degree = point_degree_minutes(self.location.EW_degree)

        return degree

    @property
    def site(self):
        """ geothing web site """
        return self.geosite.name

    @property
    def url(self):
        """ url to geothing """
        return self.geosite.url2cache(self.pid, self.code)

    # two aliases
    @property
    def latitude(self):
        """ latitude """
        return self.latitude_degree

    @property
    def longitude(self):
        """ longitude """
        return self.longitude_degree


def point_degree_minutes(degree):
    """ point degree minutes """
    couple = (None, None)
    if degree is not None:
        deg = int(degree)
        minutes = (abs(degree) - abs(deg)) * 60
        couple = (deg, minutes)

    return couple


class BlockNeedBeDivided(models.Model):
    """ BlockNeedBeDivided """
    geosite = models.ForeignKey(Geosite, on_delete=models.CASCADE)
    added = models.DateTimeField()
    bb = models.CharField(max_length=128)
    idx = models.IntegerField(db_index=True)

    class Meta:
        db_table = 'block_need_be_divided'

    def __str__(self):
        return f'Block {self.geosite}-{self.bb}'

    @classmethod
    def next_index(cls):
        """
        next index to mark executing script
        """
        return (cls.objects.aggregate(
            max_num=Max('idx')).get('max_num') or 0) + 1
