""" Carpathians models """

import math

from django.db import models
from django.utils.translation import ugettext_lazy as _

from gpsfun.utils import get_image_path


def thumbnail(width, height):
    """ thumbnail """
    max_ = 400
    factor = width / height
    if height > max_:
        height = max_
        width = int(height * factor)
    return {'width': width, 'height': height}


class GeoPoint(models.Model):
    """
    GeoPoint stores data related to point on Earth surface
    """
    latitude = models.DecimalField(
        _("latitude"), default=0, decimal_places=6, max_digits=10)
    longitude = models.DecimalField(
        _("longitude"), default=0, decimal_places=6, max_digits=10)

    def __str__(self):
        return f'point {self.latitude:10.6f}, {self.longitude:10.4f}'

    class Meta:
        db_table = 'geopoint'
        verbose_name = _("geopoint")
        verbose_name_plural = _("geopoints")

    def distance_to_point(self, point):
        """
        distance from this point to another point, km
        """
        if point is not None:
            return haversine_distance(
                self.latitude, self.longitude, point.latitude, point.longitude)
        return None

    def distance_to_coordinates(self, latitude, longitude):
        """
        distance from this point to point given by coordinates, km
        """
        return haversine_distance(
            self.latitude, self.longitude, latitude, longitude)

    @classmethod
    def degree_from_string(cls, string):
        """ get degree from string """
        items = [float(x) for x in string.split()]
        return items[0] + items[1] / 60.0 + items[2] / 3600.0


class Ridge(models.Model):
    """
    Ridge model
    """
    slug = models.SlugField(_("slug"), unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ridge'
        verbose_name = _("ridge")
        verbose_name_plural = _("ridges")

    def __str__(self):
        return f'{self.id}-{self.slug}'

    def peaks(self):
        """ ridge peaks """
        return self.peak_set.order_by('name')

    def routes(self):
        """ ridge routes """
        return Route.objects.filter(peak__ridge=self).order_by('number')


class RidgeInfoLink(models.Model):
    """
    Ridge Info Link model
    """
    ridge = models.ForeignKey(
        Ridge, on_delete=models.PROTECT, verbose_name=_("ridge"))
    link = models.URLField(_("link"), max_length=128)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'ridge_info_link'
        verbose_name = _("ridge link")
        verbose_name_plural = _("ridge links")

    def __str__(self):
        return f'{self.id}-{self.link}'


class Peak(models.Model):
    """
    Peak model
    """
    slug = models.SlugField(_("slug"), unique=True)
    ridge = models.ForeignKey(
        Ridge, on_delete=models.PROTECT, verbose_name=_("ridge"))
    name = models.CharField(max_length=64, blank=True, null=True)
    height = models.IntegerField(blank=True, null=True, default=0)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    point = models.ForeignKey(
        GeoPoint, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("point"))

    class Meta:
        db_table = 'peak'
        verbose_name = _("peak")
        verbose_name_plural = _("peaks")

    def __str__(self):
        return f'{self.id}-{self.slug}'

    def routes(self):
        """ peak routes """
        return self.route_set.order_by('number')

    def photos(self):
        """ peak photos """
        return self.peakphoto_set.order_by('id')


class PeakPhoto(models.Model):
    """
    Peak Photo model
    """
    peak = models.ForeignKey(
        Peak, on_delete=models.PROTECT, verbose_name=_("peak"))
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'peak_photo'
        verbose_name = _("peak photo")
        verbose_name_plural = _("peak photos")

    def __str__(self):
        return f'{self.id}-{self.photo}'

    @property
    def thumbnail(self):
        """ get photo thumbnail """
        return thumbnail(self.photo.width, self.photo.height)


class Route(models.Model):
    """
    Route model
    """
    peak = models.ForeignKey(
        Peak, on_delete=models.PROTECT, verbose_name=_("peak"))
    name = models.CharField(max_length=64, blank=True, null=True)
    number = models.PositiveSmallIntegerField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    map_image = models.ImageField(
        _("map"), upload_to=get_image_path, blank=True, null=True)
    difficulty = models.CharField(max_length=3, null=True)
    max_difficulty = models.CharField(max_length=16, null=True)
    length = models.IntegerField(blank=True, null=True)
    author = models.CharField(max_length=64, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    height_difference = models.IntegerField(blank=True, null=True)
    start_height = models.IntegerField(blank=True, null=True)
    descent = models.TextField(blank=True, null=True)
    ready = models.BooleanField(default=False)

    class Meta:
        db_table = 'route'
        verbose_name = _("route")
        verbose_name_plural = _("routes")

    def __str__(self):
        return f'{self.number}-{self.name}'

    def sections(self):
        """ route sections """
        return self.routesection_set.order_by('num')

    def points(self):
        """ route points """
        return self.routepoint_set.order_by('id')

    def photos(self):
        """ route photos """
        return self.routephoto_set.order_by('id')


class RouteSection(models.Model):
    """
    Route Section model
    """
    route = models.ForeignKey(
        Route, on_delete=models.PROTECT, verbose_name=_("route"))
    num = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    angle = models.CharField(max_length=32, blank=True, null=True)
    difficulty = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'route_section'
        verbose_name = _("route section")
        verbose_name_plural = _("route sections")

    def __str__(self):
        return f'{self.id}-{self.num}'

    @property
    def number(self):
        """ get section number """
        return f'R<sub>{self.num - 1}</sub>-R<sub>{self.num}</sub>'

    @property
    def details(self):
        """ get route section details """
        len_km = self.length // 1000
        len_m = self.length % 1000
        length = f'{len_m}м'
        if len_km:
            length = f'{len_km}км ' + length
        items = [length]
        if self.angle:
            items.append(self.angle)
        items.append(self.difficulty)
        return ', '.join(items)


class RoutePhoto(models.Model):
    """
    Route Photo model
    """
    route = models.ForeignKey(
        Route, on_delete=models.PROTECT, verbose_name=_("route"))
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'route_photo'
        verbose_name = _("route photo")
        verbose_name_plural = _("route photos")

    def __str__(self):
        return f'{self.id}-{self.photo}'

    @property
    def thumbnail(self):
        """ get photo thumbnail """
        return thumbnail(self.photo.width, self.photo.height)


class RoutePoint(models.Model):
    """
    Route Point model
    """
    route = models.ForeignKey(
        Route, on_delete=models.PROTECT, verbose_name=_("route"))
    point = models.ForeignKey(
        GeoPoint, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("point"))
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'route_point'
        verbose_name = _("route point")
        verbose_name_plural = _("route points")

    def __str__(self):
        return f'{self.route.id}-{self.point}'


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    It calculates distance between two points (km).
    https://en.wikipedia.org/wiki/Haversine_formula
    Test: distance between Red Square (55.7539° N, 37.6208° E)
    and Hermitage (59.9398° N, 30.3146° E) equals 634.569km
    """
    earth_radius = 6371.0

    lon1, lat1, lon2, lat2 = map(math.radians, (lon1, lat1, lon2, lat2))

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    aaa = math.sin(dlat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2) ** 2

    return earth_radius * 2 * math.asin(math.sqrt(aaa))
