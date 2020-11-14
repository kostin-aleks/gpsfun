from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.flatpages.models import FlatPage

class TextBlock(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    slug = models.SlugField()
    text = models.TextField(blank=True,null=True)
    order = models.IntegerField(default=50)
    is_displayed = models.BooleanField(default=True)

    def __unicode__(self):
        return '<ContentBlock: %s>' % self.slug


class Link(models.Model):
    href = models.CharField(max_length=100)
    title = models.CharField(max_length=100, core=True)
    order = models.IntegerField(default=50)
    css_class = models.CharField(max_length=50,blank=True,null=True)
    link_list = models.ForeignKey('LinkList',edit_inline=True)


class LinkList(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    slug = models.SlugField()
    order = models.IntegerField(default=50)
    is_displayed = models.BooleanField(default=True)
    css_class = models.CharField(max_length=50,blank=True,null=True)

    def links(self):
        return Link.objects.filter(link_list=self).order_by('order')
    
    def __unicode__(self):
        return '<LinkList: %s>' % self.slug


class TreeBranch(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    uplink = models.ForeignKey('TreeBranch', blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    is_displayed = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=50)

class FlatPageImage(models.Model):
    image = models.ImageField(upload_to='flatpage_images')
    page = models.ForeignKey(FlatPage)
    
