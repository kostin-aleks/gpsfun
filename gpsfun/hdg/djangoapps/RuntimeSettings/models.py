import types, datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal

TYPE_CHOICE = (
    ('int', _('Integer')),
    ('str', _('String')),
    ('datetime', _('DateTime')),
    ('float', _('Float')),
    ('bool', _('Boolean'))
    )


TYPES = {
    'int': [types.IntType],
    'str': [types.StringType, types.UnicodeType],
    'datetime': [type(datetime.datetime.now())],
    'float': [types.FloatType, type(Decimal)],
    'bool': [types.BooleanType]}


class RuntimeCategory(models.Model):
    name = models.CharField(max_length=54)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'runtime_category'
        verbose_name= _('runtime category')
        verbose_name_plural= _('runtime categories')


class RuntimeVariable(models.Model):
    category = models.ForeignKey(RuntimeCategory)
    key = models.CharField(_('key'), max_length=32, unique=True)
    key_type = models.CharField(_('key type'), max_length=8, choices=TYPE_CHOICE)
    description = models.TextField(_('description'), null=True, blank=True)

    value_int = models.IntegerField(_('integer value'), null=True, blank=True)
    value_str = models.TextField(_('string value'), null=True, blank=True)
    value_datetime = models.DateTimeField(_('datetime value'), null=True, blank=True)
    value_float = models.FloatField(_('float value'), null=True, blank=True)
    value_bool = models.NullBooleanField(_('boolean value'), blank=True)

    default_value_int = models.IntegerField(_('default integer value'), null=True, blank=True)
    default_value_str = models.TextField(_('default string value'), null=True, blank=True)
    default_value_datetime = models.DateTimeField(_('default datetime value'), null=True, blank=True)
    default_value_float = models.FloatField(_('default float value'), null=True, blank=True)
    default_value_bool = models.NullBooleanField(_('default boolean value'), blank=True)

    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def getvalue(cls, key, category_name=None):
        kwargs=dict(key=key)
        if category_name:
            kwargs['category']=RuntimeCategory.objects.get(name=category_name)
        return RuntimeVariable.objects.get(**kwargs).value

    class Meta:
        db_table = u'runtime_variable'
        # verbose_name_plural= 'runtime vara'
        verbose_name= _('runtime variable')
        verbose_name_plural= _('runtime variables')


    def _get_value(self):
        rc = getattr(self,'value_%s'%self.key_type)
        if rc is None:
            rc = self.default_value
        return rc

    def _set_value(self, value):
        is_set=False
        for ktype in TYPES:
            if type(value) in TYPES[ktype]:
                self.key_type=ktype
                setattr(self,'value_%s' % self.key_type, value)
                is_set=True
        if not is_set:
            raise TypeError(_("Variable can not be set %s") % value)

    value = property(_get_value, _set_value)

    def _get_default_value(self):
        return getattr(self,'default_value_%s'%self.key_type)
    default_value = property(_get_default_value)


    def localized_description(self):
        if self.description:
            return _(self.description)
        else:
            return ''
