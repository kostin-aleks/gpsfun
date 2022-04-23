"""
widgets
"""
import datetime
import copy
from itertools import chain
import types

from django.utils.safestring import mark_safe
from django.template import Context, loader
from django.utils.encoding import force_unicode

try:
    # just for check version of Django
    from django.forms import Manipulator as _OldManipulator
    from django import newforms as forms
except ImportError:
    from django import forms


class TextInputPopup(forms.TextInput):
    """ TextInputPopup """

    def __init__(self, url, frame_id='popup_div', *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        if 'onkeyup' not in attrs:
            attrs.update({
                'onkeyup': mark_safe(f"textinput_popup_keyup(this,'{url}','{frame_id}');")})
        attrs.update({'autocomplete': 'off'})
        super(TextInputPopup, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        """ render """
        return super(TextInputPopup, self).render(name, value, attrs)


class DateWidget(forms.TextInput):
    """ DateWidget """

    def __init__(self, attrs=None, format=None):
        super(DateWidget, self).__init__(attrs)
        self.format = format

    def render(self, name, value, attrs=None):
        """ render """
        if self.format and isinstance(value, datetime.date):
            value = value.strftime(self.format)

        return super(DateWidget, self).render(name, value, attrs)


class FormWidget(forms.Widget):
    """ FormWidget """

    def __init__(self, subform=None, template=None, attrs=None, buttons=None):
        self.template = template or 'forms/form_widget.html'

        self.buttons = buttons or []

        if isinstance(subform, type):
            subform = subform()

        self.subform = subform

        super(FormWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        """ render """
        subform = copy.deepcopy(self.subform)

        data = {}
        if value is not None:
            data = value
            subform.is_bound = True

        subform.inital = {}
        subform.data = data

        template = self.template
        if hasattr(subform, 'template'):
            template = subform.template

        template = loader.get_template(template)

        return template.render(Context({
            'widget': self,
            'subform': subform,
        }))

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        value = dict()
        if data.has_key(name):
            [value.update({f"{name}-{k}": v}) for k, v in data[name].iteritems()]
            return value

        value = dict()
        #[ k.startswith(self.subform.prefix) and value.update( {k: v[0]} ) for k,v in data.iteritems() ]
        for k, v in data.iteritems():
            if k.startswith(self.subform.prefix):
                if type(value) == types.ListType:
                    value.update({k: v[0]})
                else:
                    value.update({k: v})

        for k, v in value.iteritems():
            if v in forms.fields.EMPTY_VALUES:
                value[k] = None

        return value


class RangeWidget(forms.MultiWidget):
    """ RangeWidget """

    def __init__(self, attrs=None):
        widgets = (forms.TextInput(attrs=attrs), forms.TextInput(attrs=attrs))
        super(RangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        """ decompress """
        if value:
            return [value[0], value[1]]
        return [None, None]


class LabelWidget(forms.Select):
    """ LabelWidget """

    def render(self, name, value, attrs=None, choices=()):
        """ render """
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type="text", name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)

        final_attrs['type'] = 'hidden'

        out_str = u'<span>%s</span>' % (value)
        if len(self.choices) > 0:
            for option_value, option_label in chain(self.choices, choices):
                if option_value == value:
                    out_str = u'<span>%s</span>' % (option_label)
                    break

        out_str += u'<input %s/>' % (forms.util.flatatt(final_attrs))
        return mark_safe(out_str)


##
# Hologramm widget used for execute AJAX request to the server
# and after success responce with Key_ID, retrieve image from the server
#
# Argument:
# jsfunction - name of the javascript function;
#              this function will calling with next arguments:
#                   fields_id - ID of hidden field where need to
#                               store request ID
#                   image_id - ID of target image
#
# "jsfunction" will calling after page load with Mochikit function
#
class Hologramm(forms.Widget):
    """ Hologramm """
    input_type = 'hologram'

    def __init__(self, jsfunction, default_img='', attrs=None):
        self.jsfunction = jsfunction
        self.default_img = default_img
        super(Hologramm, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        """ render """
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)

        final_attrs['type'] = 'hidden'

        id_ = final_attrs['id']
        img_ = self.default_img
        func_ = self.jsfunction
        out_str = f'<input {forms.util.flatatt(final_attrs)}/>'
        out_str += f"<img id=\"img_{id_}\" src=\"{img_}\"\><script>{func_}('{id_}','img_{id_}', '{value}');</script>"

        return mark_safe(out_str)


class SelectOrAdd(forms.Select):

    def __init__(self, attrs=None, choices=(), onclick=None, img=None):
        super(SelectOrAdd, self).__init__(attrs, choices)
        self._img = img or '/s/img/16x16/add.png'
        self._onclick = onclick or 'select_or_add'

    def render(self, name, value, attrs=None, choices=()):
        """ render """
        rc = super(SelectOrAdd, self).render(name, value, attrs, choices)

        img = f'<a href="" onclick="return {self._onclick}(this, \'{name}\')"><img src="{self._img}"></a>'
        return rc + mark_safe(img)
