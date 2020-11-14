from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.conf import settings

class TextBlock(models.Model):
    title = models.CharField(_('Title'), max_length=255,blank=True,null=True)
    slug = models.SlugField(_('Slug'))
    text = models.TextField(_('Text'), blank=True,null=True)
    order = models.IntegerField(_('Order'), default=50)
    is_displayed = models.BooleanField(_('Is displayed'), default=True)

    class Meta:
        db_table = 'cms_textblock'
        verbose_name = _('text block')
        verbose_name_plural = _('text blocks')

    def __unicode__(self):
        return '<ContentBlock: %s>' % self.slug


class Link(models.Model):
    url = models.CharField(_('URL'), max_length=100)
    title = models.CharField(_('Title'), max_length=100)
    order = models.IntegerField(_('Order'), default=50)
    css_class = models.CharField(_('CSS class'), max_length=50,blank=True,null=True)
    link_list = models.ForeignKey('LinksList')

    class Meta:
        db_table = 'cms_link'
        verbose_name = _('link')
        verbose_name_plural = _('links')

    def save(self, *args, **kwargs):
        from DjHDGutils.cache import invalidate_template_cache
        invalidate_template_cache(self.link_list.slug)
        super(Link, self).save(*args, **kwargs)

class LinksList(models.Model):
    title = models.CharField(_('Title'), max_length=255,blank=True,null=True)
    slug = models.SlugField(_('Slug'))
    order = models.IntegerField(_('Order'), default=50)
    is_displayed = models.BooleanField(_('Is displayed'), default=True)
    css_class = models.CharField(_('CSS class'), max_length=50,blank=True,null=True)

    class Meta:
        db_table = 'cms_linkslist'
        verbose_name = _('links list')
        verbose_name_plural = _('links lists')

    def links(self):
        return Link.objects.filter(link_list=self).order_by('order')

    def __unicode__(self):
        return _('<LinkList: %s>') % self.slug


class Navigation(models.Model):
    short_title = models.CharField(_('Short Title'), max_length=50)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    uplink = models.ForeignKey('Navigation', blank=True, null=True)
    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)
    is_displayed = models.BooleanField(_('Is displayed'), default=True)
    sort_order = models.IntegerField(_('Sort order'), default=50)

    def content_object_info(self):
        return unicode(self.content_object)

    class Meta:
        db_table = 'cms_objecttree'
        verbose_name = _('navigation branch')
        verbose_name_plural = _('navigation tree')

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def __unicode__(self):
        return self.short_title

class SiteSettings(models.Model):
    site = models.ForeignKey(Site, unique=True)
    allowed_content_types = models.ManyToManyField(ContentType)

    def __unicode__(self):
        return _(u'Settings for %s') % self.site

    class Meta:
        db_table = 'simplecms_sitesettings'
        verbose_name = _('site settings')
        verbose_name_plural = _('site settings')


class FlatPageImage(models.Model):
    image = models.ImageField(_('Image'), upload_to='flatpage_images')
    page = models.ForeignKey(FlatPage)


class FlatPageFile(models.Model):
    fpfile = models.FileField(_('File'), upload_to='flatpage_files')
    title = models.CharField(_('Title'), max_length=255,blank=True,null=True)
    page = models.ForeignKey(FlatPage)


class CSSDesignSkin(models.Model):
    site = models.ForeignKey(Site, unique=True)
    title = models.CharField(max_length=100)
    css_file = models.FilePathField(path=settings.MEDIA_ROOT+'css/skins/')
    pageid_regexp = models.CharField(max_length=50, blank=True, null=True)
    sort_order = models.IntegerField(default=50)

    class Meta:
        db_table = 'simplecms_cssdesignskin'
        verbose_name = _('CSS Design Skin')
        verbose_name_plural = _('CSS Design Skins')

# TODO FIXME
# from django.db.models import signals
# def update_nav_title(sender, instance, created, raw, *args, **kwargs):
#     """ sync title once its changed first time """
#     naventries = Navigation.objects.filter(object_id = instance.id,
#                                     content_type = ContentType.objects.get_for_model(FlatPage))
#     if len(naventries)==1:
#         nav=naventries[0]
#         if nav.short_title.startswith('New object'):
#             nav.short_title = instance.title
#             nav.save()

# signals.post_save.connect(update_nav_title)


