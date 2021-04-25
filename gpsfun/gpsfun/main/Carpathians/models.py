from django.db import models
from django.utils.translation import ugettext_lazy as _
from gpsfun.utils import get_image_path, media_url, image_url


class GeoPoint(models.Model):
    """
    GeoPoint stores data related to point on Earth surface
    """
    latitude = models.DecimalField(
        _("latitude"), default=0, decimal_places=6, max_digits=10)
    longitude = models.DecimalField(
        _("longitude"), default=0, decimal_places=6, max_digits=10)

    def __str__(self):
        return 'point {:10.6f}, {:10.4f}'.format(self.latitude, self.longitude)

    class Meta:
        db_table = 'geopoint'
        verbose_name = _("geopoint")
        verbose_name_plural = _("geopoints")

    def distance_to_point(self, P):
        """
        distance from this point to another point, km
        """
        if P is not None:
            return haversine_distance(
                self.latitude, self.longitude, P.latitude, P.longitude)

    def distance_to_coordinates(self, latitude, longitude):
        """
        distance from this point to point given by coordinates, km
        """
        return haversine_distance(
            self.latitude, self.longitude, latitude, longitude)


class Ridge(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    map_image = models.ImageField(
        _("map"), upload_to=get_image_path, blank=True, null=True)

    class Meta:
        db_table = 'ridge'
        verbose_name = _("ridge")
        verbose_name_plural = _("ridges")

    def __str__(self):
        return '%s-%s' % (self.id, self.name)


class RidgeInfoLink(models.Model):
    ridge = models.ForeignKey(
        Ridge, on_delete=models.PROTECT, verbose_name=_("ridge"))
    link = models.URLField(_("link"), max_length=128, blank=True)
    description = models.CharField(max_length=128)

    class Meta:
        db_table = 'ridge_info_link'
        verbose_name = _("ridge link")
        verbose_name_plural = _("ridge links")

    def __str__(self):
        return '%s-%s' % (self.id, self.link)


class Peak(models.Model):
    ridge = models.ForeignKey(
        Ridge, on_delete=models.PROTECT, verbose_name=_("ridge"))
    name = models.CharField(max_length=64)
    height = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    map_image = models.ImageField(
        _("map"), upload_to=get_image_path, blank=True, null=True)
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    point = models.ForeignKey(
        GeoPoint, null=True, on_delete=models.SET_NULL, verbose_name=_("point"))

    class Meta:
        db_table = 'peak'
        verbose_name = _("peak")
        verbose_name_plural = _("peaks")

    def __str__(self):
        return '%s-%s' % (self.id, self.name)


class PeakPhoto(models.Model):
    peak = models.ForeignKey(
        Peak, on_delete=models.PROTECT, verbose_name=_("peak"))
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    description = models.CharField(max_length=128)

    class Meta:
        db_table = 'peak_photo'
        verbose_name = _("peak photo")
        verbose_name_plural = _("peak photos")

    def __str__(self):
        return '%s-%s' % (self.id, self.photo)


class Route(models.Model):
    peak = models.ForeignKey(
        Peak, on_delete=models.PROTECT, verbose_name=_("peak"))
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    difficulty = models.CharField(max_length=32)
    length = models.IntegerField(blank=True, null=True)
    author = models.CharField(max_length=64, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    height_difference = models.IntegerField(blank=True, null=True)
    start_height = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'route'
        verbose_name = _("route")
        verbose_name_plural = _("routes")

    def __str__(self):
        return '%s-%s' % (self.id, self.name)


class RouteSection(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.PROTECT, verbose_name=_("route"))
    num = models.IntegerField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    angle = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'route_section'
        verbose_name = _("route section")
        verbose_name_plural = _("route sections")

    def __str__(self):
        return '%s-%s' % (self.id, self.num)


class RoutePhoto(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.PROTECT, verbose_name=_("route"))
    photo = models.ImageField(
        _("photo"), upload_to=get_image_path, blank=True, null=True)
    description = models.CharField(max_length=128)

    class Meta:
        db_table = 'route_photo'
        verbose_name = _("route photo")
        verbose_name_plural = _("route photos")

    def __str__(self):
        return '%s-%s' % (self.id, self.photo)


