"""
new forms
"""
import copy
import hashlib

from django.template import Context, loader
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe

try:
    # just for ident version of Django
    from django import newforms as forms
except ImportError:
    from django import forms


class BoundRow(object):
    """ BoundRow """

    def __init__(self, table, row, row_id=None, is_bound=False):
        self.table = table
        self.row = row
        self.row_id = row_id
        self._errors = None
        self.is_bound = is_bound

    def __str__(self):
        return f"<BoundRow num:{self.row_id} rowset: {self.rowset}>"

    def __getitem__(self, key):
        field = self.table.get_fields(key)
        if field is None:
            raise KeyError(key)
        data = field.widget.value_from_datadict(self.row, [], key)
        return field.clean(data)

    def is_deleted(self):
        """ is deleted ? """
        return (self.row.get('rowdelete', '0') == '1')

    def is_modified(self):
        """ is modified ? """
        return (self.crc != self.original_crc)

    def is_new(self):
        """ is new ? """
        return (self.rowset < 0)

    def get_data(self, name, widget=None):
        """ get data """
        if isinstance(self.row, dict):
            if widget:
                data = widget.value_from_datadict(self.row, [], name)
            else:
                data = self.row.get(name, None)

        elif isinstance(self.row, models.Model) and hasattr(self.row, name):
            data = getattr(self.row, name)
            if callable(data):
                data = data()
        else:
            data = None

        return data

    def _td_attrs(self, widget):
        """ td attributes """
        attrs = {}
        for key, value in widget.attrs.items():
            if key.startswith('td_'):
                attrs.update({key[3:]: value})
        return attrs

    def _clear_td_attrs(self, widget):
        """ clear td attributes """
        attrs = {}
        for key, value in widget.attrs.items():
            if not key.startswith('td_'):
                attrs.update({key: value})
        return attrs

    def _get_rowset(self):
        """ get row set """
        try:
            rowset = int(self.get_data('rowset'))
        except:
            rowset = self.row_id
        return rowset
    rowset = property(_get_rowset)

    def _get_prefix(self):
        """ get prefix """
        return self.table.prefix
    prefix = property(_get_prefix)

    def _get_crc(self):
        """ get crc """
        m = hashlib.md5()
        for field in self.row:
            data = self.row[field]
            data = str(data)
            m.update(data)
        return m.hexdigest()

    crc = property(_get_crc)

    def _get_original_crc(self):
        """ get original crc """
        if isinstance(self.row, models.Model):
            return self.crc

        return self.row.get('rowcrc', self._get_crc())
    original_crc = property(_get_original_crc)

    def iter_cells(self):
        """ iterate cells """
        for name, field in self.table.fields.items():
            if field.widget.is_hidden:
                continue
            widget = copy.deepcopy(field.widget)
            widget.attrs = self._clear_td_attrs(widget)
            extra_attrs = {}
            field_name = name
            if isinstance(widget, forms.CheckboxInput):
                extra_attrs['value'] = f"{self.row_id}"
                field_name += ":checkbox"

            value = self.get_data(name, widget)
            errors = False
            if self.is_bound:
                try:
                    value = field.clean(value)
                except forms.util.ValidationError as e:
                    errors = e.messages

            yield {
                'value': value,
                'widget': widget,
                'cell_attr': mark_safe(
                    forms.util.flatatt(self._td_attrs(field.widget))),
                'html': mark_safe(
                    widget.render(
                        f"{self.table.prefix}:{field_name}",
                        value,
                        extra_attrs)),
                'errors': errors
            }

    def iter_hidden_cells(self):
        """ iterate hidden cells """
        for name, field in self.table.fields.items():
            if not field.widget.is_hidden:
                continue
            widget = copy.deepcopy(field.widget)
            widget.attrs = self._clear_td_attrs(widget)
            extra_attrs = {}
            field_name = name

            value = self.get_data(name, widget)

            yield {
                'value': value,
                'widget': widget,
                'cell_attr': '',
                'html': mark_safe(
                    widget.render(
                        f"{self.table.prefix}:{field_name}",
                        value,
                        extra_attrs))
            }

    def _get_errors(self):
        """ Returns an ErrorDict for the data provided for the form """
        if self._errors is None:
            self.full_clean()
        return self._errors
    errors = property(_get_errors)

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = forms.util.ErrorDict()
        if not self.is_bound or self.is_deleted():  # Stop further processing.
            return
        self.cleaned_data = {}
        for name, field in self.table.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            value = self.get_data(name, field.widget)
            try:
                value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self.table, 'clean_%s' % name)(self.row, self.rowset)
                    self.cleaned_data[name] = value
            except forms.util.ValidationError as e:
                self._errors[name] = e.messages
                if name in self.cleaned_data:
                    del self.cleaned_data[name]

    def is_valid(self):
        """
        Returns True if the form has no errors. Otherwise, False. If errors are
        being ignored, returns False.
        """
        return self.is_bound and not bool(self.errors)


class BaseTable(object):
    """ BaseTable """

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=forms.utils.ErrorList,
                 can_delete_row=False, can_append_row=False):
        self.is_bound = data is not None or files is not None
        self.data = data
        self.initial = initial or []
        self.files = files or {}
        self.auto_id = auto_id
        self.prefix = prefix or "table"
        self.error_class = error_class
        self._errors = None  # Stores the errors after clean() has been called.
        self.can_delete_row = can_delete_row
        self.can_append_row = can_append_row

        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        self.fields = copy.deepcopy(self.base_fields)

    def __str__(self):
        return self.render()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for rownum, row in enumerate(self.data):
            yield BoundRow(self, row, rownum, self.is_bound)

    def _get_errors(self):
        """ Returns an ErrorDict for the data provided for the form """
        if self._errors is None:
            self.full_clean()
        return self._errors
    errors = property(_get_errors)

    def full_clean(self):
        """ full clean """
        self._errors = {}
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = {}

        for row in self:
            if not row.is_valid():
                self._errors[row.rowset] = row.errors

    def get_fields(self, field_name):
        """ get fields """
        if field_name not in self.fields:
            return None
        return self.fields[field_name]

    def is_valid(self):
        """
        Returns True if the form has no errors. Otherwise, False. If errors are
        being ignored, returns False.
        """
        return self.is_bound and not bool(self.errors)

    def add_initial_prefix(self, field_name):
        """
        Add a 'initial' prefix for checking dynamic initial values
        """
        return u'initial-%s' % self.add_prefix(field_name)

    def add_prefix(self, field_name):
        """
        Returns the field name with a prefix appended, if this Form has a
        prefix set.

        Subclasses may wish to override.
        """
        return self.prefix and (f'{self.prefix}-{field_name}') or field_name

    def set_post(self, data):
        """ set post """
        if hasattr(data, 'lists'):
            data = data.lists()

        source = dict()
        prefix = "%s:" % self.prefix
        [k.startswith(prefix) and source.update({k[len(prefix):]: v}) for k, v in data]

        assert('rowset' in source)

        target = list()
        for i, row_key in enumerate(source['rowset']):
            # test for data rows, and skip all additional helper rows
            try:
                int(row_key)
            except ValueError:
                continue

            row = dict()
            for k, v in source.items():
                if k.endswith(':checkbox'):
                    if row_key in v:
                        row.update({k[:k.index(':checkbox')]: True})
                    continue
                if len(v) < i:
                    continue
                row.update({k: v[i]})
            target.append(row)

        self.data = target
        self.is_bound = True

    def iter_head(self):
        """ iterate head """
        for name, field in self.fields.items():
            bf = forms.forms.BoundField(self, field, name)
            if bf.is_hidden:
                continue

            label = ''
            if bf.label:
                label = escape(bf.label)

            yield {
                'id': self.add_prefix(name),
                'label': label}

    def iter_rows(self):
        """ iterate rows """
        soruce = self.data or self.initial
        for rownum, row in enumerate(soruce):
            yield BoundRow(self, row, rownum, self.is_bound)

    def iter_template_row(self):
        """ iterate template row """
        yield BoundRow(self, {}, 'template')

    def render(self):
        """ render """
        template = loader.get_template('forms/table.html')

        return template.render(
            Context({'table': self}))


class TemplatedTable(BaseTable):
    """ A collection of Fields, plus their associated data. """
    # This is a separate class from BaseForm in order to abstract the way
    # self.fields is specified. This class (Form) is the one that does the
    # fancy metaclass stuff purely for the semantic sugar -- it allows one
    # to define a form using declarative syntax.
    # BaseForm itself has no way of designating self.fields.
    __metaclass__ = forms.forms.DeclarativeFieldsMetaclass


class TemplatedForm(forms.Form):
    """
    template forms/form.html:
    % for field in bound_fields %}
    {% include "forms/field.html" %}
    {% endfor %}


    template forms/field.html:
    <tr{% if field.errors %} class="errors" {% endif%}>
    <th>
    <label for="id_{{ field.name }}">{{ field.label }}{% if field.field.required %}<span class="required">*</span>{% endif %}:</label>
    </th>
    <td>
    {{ field }}
    {% if field.errors %}{{ field.errors }}{% endif %}
    {% if field.help_text %}
    <p class="helptext">({{ field.help_text }})</p>
    {% endif %}
    </td>
    </tr>
    """

    def __init__(self, *kargs, **kwargs):
        my_kwargs = {}

        self.request = None
        self._template = None

        # hack with iterators, because deepcopy not workin on production server
        for key, value in kwargs.items():
            if key == 'request':
                self.request = value
            elif key == 'template':
                self._template = value
            else:
                my_kwargs[key] = value

        super(TemplatedForm, self).__init__(*kargs, **my_kwargs)

        if (hasattr(self, 'custom_init')):
            custom_init = getattr(self, 'custom_init')
            if callable(custom_init):
                custom_init()

    def get_template_name(self):
        """ get template name """
        return self._template or "forms/form.html"

    def output_via_template(self):
        """ Helper function for fieldsting fields data from form. """
        def create_bound_field(field, name):
            bound_field = forms.forms.BoundField(self, field, name)
            if hasattr(field, 'not_visible'):
                bound_field.not_visible = field.not_visible
            return bound_field

        bound_fields = [create_bound_field(field, name) for name, field
                        in self.fields.items()]

        c = Context(dict(form=self, bound_fields=bound_fields))
        t = loader.get_template(self.get_template_name())

        return t.render(c)

    def __unicode__(self):
        return self.output_via_template()

    def as_template(self):
        """ as template """
        return self.output_via_template()
