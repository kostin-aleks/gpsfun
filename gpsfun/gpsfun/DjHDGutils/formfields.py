"""
class AddTripForm(RequestModelForm):
    start_time = SplitDateTimeJSField(label=_('Start Time'))
    class Meta:
        model = Trip
from: http://stackoverflow.com/questions/38601/using-django-time-date-widgets-in-custom-form
"""

from django import forms
from django.template.loader import render_to_string


class SplitDateTimeJSField(forms.SplitDateTimeField):
    """ SplitDateTimeJSField """

    def __init__(self, *args, **kwargs):
        super(SplitDateTimeJSField, self).__init__(*args, **kwargs)
        self.widget.widgets[0].attrs = {'class': 'vDateField'}
        self.widget.widgets[1].attrs = {'class': 'vTimeField'}


class FakeField(forms.Field):
    """
       id - html tag id (can ba used in template)
    """

    custom_render = True
    template = None
    id = None

    def __init__(self, id=None, *kargs, **kwargs):
        """ attrs - dictionary with attributes of html element """

        kwargs['required'] = False
        self.id = id

        super(FakeField, self).__init__(*kargs, **kwargs)

    def render(self):
        """ render """
        if self.template:
            return render_to_string(self.template,
                                    {'field': self})
        else:
            return None

    def __unicode__(self):
        return self.render()

    def id_attr(self):
        """ return rendered id=self.id attribute if not empty """

        if self.id:
            return 'id=%s' % self.id
        else:
            return None


class GroupHeaderField(FakeField):
    """ GroupHeaderField """
    template = "forms/form_field_header.html"
