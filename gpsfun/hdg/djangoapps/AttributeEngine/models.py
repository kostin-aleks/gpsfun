from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

""" This module makes it easy for site administrator to relate common
attribute types to a database object - for example this is used to
configure additional Product fields """

ATTRIBUTE_TYPES = (('str', _('String')), # Limit list to very common/generic types
                   ('txt', _('Text')),
                   ('int', _('Integer')),
                   ('dat', _('Date')),
                   ('bol', _('Boolean')),
                   ('dec', _('Decimal')))


class AttributeGroup(models.Model):
    name = models.CharField(_('Name'), max_length=255)

    def __unicode__(self):
        return "%d/%s" % (self.id, self.name)

    class Meta:
        db_table = 'attr_group'
        verbose_name = _(u"Attribute Group")
        verbose_name_plural = _(u"Attribute Groups")

class AttributeGroupField(models.Model):
    attr_group = models.ForeignKey(AttributeGroup)
    name = models.CharField(max_length=255)
    sort_order = models.SmallIntegerField(default=50)
    attr_type = models.CharField(max_length=3, choices=ATTRIBUTE_TYPES)
    picture = models.ImageField(upload_to='data/attrgrp_pics', blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'attr_group_field'
        unique_together = ('attr_group', 'name')
        verbose_name = _(u"Attribute Group Field")
        verbose_name_plural = _(u"Attribute Group Fields")

class TextAttribute(models.Model):
    """ Some databases (namely MySQL) are inefficient when storing Blob
    values in same record. So we moved those records out and fetch only
    on demand"""
    value = models.TextField(_('value'))

    class Meta:
        db_table = 'text_attr'
        verbose_name = _(u"Text Attribute")
        verbose_name_plural = _(u"Text Attributes")

class Attribute(models.Model):
    """ We are trading record size for speed. It is much more important
    to have fast database with a cost of little overhead """
    attr_type = models.CharField(_('Attribute Type'), max_length=3, choices=ATTRIBUTE_TYPES)
    attr_group = models.ForeignKey(AttributeGroup)
    attr_group_field = models.ForeignKey(AttributeGroupField)
    value_int = models.IntegerField(_('Integer Value'), null=True, blank=True)
    value_char = models.CharField(_('Charactar Value'), max_length=255, null=True, blank=True)
    value_text = models.ForeignKey(TextAttribute, null=True, blank=True)
    value_datetime = models.DateTimeField(_('Datetime value'), null=True, blank=True)
    value_decimal = models.DecimalField(_('Decimal value'), max_digits=settings.DECIMAL_DIGITS,
                                        blank=True,
                                        null=True,
                                        decimal_places=settings.DECIMAL_PLACES)

    def _value_get(self):
        if self.attr_type == 'str':
            return self.value_char
        elif self.attr_type == 'txt':
            return 'FIXME: textarea'
        elif self.attr_type == 'int':
            return self.value_int
        elif self.attr_type == 'dat':
            return self.value_datetime
        elif self.attr_type == 'bol':
            return self.value_int == 1
        elif self.attr_type == 'dec':
            return self.value_decimal
        else:
            raise ValueError(_('type %s not found') % self.attr_type)

    def _value_set(self, value):
        if self.attr_type == 'str':
            self.value_char = value
        elif self.attr_type == 'txt':
            print 'FIXME: textarea'
        elif self.attr_type == 'int':
            self.value_int = value
        elif self.attr_type == 'dat':
            self.value_datetime = value
        elif self.attr_type == 'bol':
            self.value_int == value
        elif self.attr_type == 'dec':
            self.value_decimal = value
        else:
            raise ValueError(_('type %s not found') % self.attr_type)

    value=property(_value_get, _value_set)


    class Meta:
        abstract = True



def update_child_attributes(sender, **kwargs): # FIXME: add handing of 'type' change
    """ For performance reasons, we use redunant data in Attribute instances (group, type).
    Now, when attribute group or type getting changed via django admin, we need to update
    corresponding attributes in child objects"""
    agfield = kwargs['instance']
    if agfield.id:
        from django.db import connection
        from django.db.models.loading import get_models
        cursor = connection.cursor()
        cursor.execute('select attr_group_id from attr_group_field where id=%s' % agfield.id)
        try:
            old_agroup_id = cursor.fetchone()[0]
        except TypeError:
            old_agroup_id = None

        if agfield.attr_group.id != old_agroup_id:
            for model in get_models():
                found = True
                for fieldname in ['attr_type', 'attr_group', 'attr_group_field']:
                    if fieldname not in [f.name for f  in model._meta.fields]:
                        found = False
                        break
                if found:
                    objects = model.objects.filter(attr_group=old_agroup_id,
                                                   attr_group_field=agfield.id)
                    objects.update(attr_group=agfield.attr_group)

pre_save.connect(update_child_attributes, sender=AttributeGroupField)
