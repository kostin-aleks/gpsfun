from django.utils.safestring import mark_safe
from django.urls import reverse, NoReverseMatch
from django.db.models.manager import Manager


class BaseWidget(object):
    creation_counter = 0

    def __init__(self, label, refname=None, width=None, title_attr=None, cell_attr=None):
        self.label = label
        self.refname = refname
        self.title_attr = title_attr
        self.cell_attr = cell_attr
        self.width = width

        # Increase the creation counter, and save our local copy.
        self.creation_counter = BaseWidget.creation_counter
        BaseWidget.creation_counter += 1

    def html_title(self):
        return self.label

    def _recursive_value(self, row, keylist):
        value = None
        if hasattr(row, keylist[0]):
            value = getattr(row, keylist[0])
            if callable(value):
                value = value()
            if len(keylist) > 1:
                return self._recursive_value(value, keylist[1:])

        return value

    def get_value(self, row, refname=None, default=None):
        if refname is None and self.refname is None:
            return default

        value = self._recursive_value(row, (refname or self.refname).split('__'))
        if value is not None:
            if isinstance(value, Manager):
                return value.all()

            return value
        return default

    def html_cell(self, row_index, row):
        value = self.get_value(row)
        if value is None:
            value = '&nbsp'
        return mark_safe(value)


    def _dict2attr(self, attr):
        if not attr:
            return u""

        rc = u""
        for key,value in attr.iteritems():
            rc += u' %s="%s"'%(key,value)

        return mark_safe(rc)


    def html_title_attr(self):
        return self._dict2attr(self.title_attr)


    def html_cell_attr(self):
        return self._dict2attr(self.cell_attr)



class LabelWidget(BaseWidget):
    pass

class DateTimeWidget(BaseWidget):
    def __init__(self, *kargs, **kwargs):
        self.format = "%d/%m/%y %H:%M"

        _kwargs = {}
        for key,value in kwargs.iteritems():
            if key == 'format':
               self.format = value
            else:
               _kwargs[key] = value

        super(DateTimeWidget, self).__init__(*kargs, **_kwargs)


    def html_cell(self, row_index, row):
        value = self.get_value(row)
        if value:
            return value.strftime(self.format)
        return mark_safe(u'&nbsp;')


class HrefWidget(BaseWidget):
    def __init__(self, *kargs, **kwargs):
        self.href = None
        self.reverse = None
        self.reverse_column = 'id'
        my_kwargs = {}

        for key, value in kwargs.iteritems():
            if key == 'href':
                self.href = value
            elif key == 'reverse':
                self.reverse = value
            elif key == 'reverse_column':
                self.reverse_column = value
            else:
                my_kwargs[key] = value

        super(HrefWidget, self).__init__(*kargs, **my_kwargs)


    def html_cell(self, row_index, row):
        href = ''
        value = super(HrefWidget, self).html_cell(row_index, row)
        if self.reverse:
            try:
                href = reverse(self.reverse, args=[self.get_value(row, self.reverse_column), ])
            except NoReverseMatch, e:
                href = "#NoReverseMatch"

        return mark_safe(u"<a href='%s'>%s</a>"%(href,value))
