"""
forms related to app user
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from gpsfun.DjHDGutils.newforms import TemplatedForm
from gpsfun.main.GeoName.models import populate_country_subject_city


class CityForm(TemplatedForm):
    """ Form City """
    country = forms.ChoiceField(
        required=False,
        label=_('Country'),
        widget=forms.Select(attrs={'id': 'id_select_country',
                                   'onchange': 'CityWidget.reload_subjects(this);'
                                   }))
    subject = forms.ChoiceField(
        required=False,
        label=_('Admin Subject'),
        widget=forms.Select(attrs={'id': 'id_select_subject',
                                   'onchange': 'CityWidget.reload_cities(this);'
                                   }))
    city = forms.ChoiceField(
            required=False,
            label=_('City'),
            widget=forms.Select(attrs={'id': 'id_select_city',
                                       'onchange': 'CityWidget.chosen_city(this);'
                                       }))


    def __init__(self, *kargs, **kwargs):
        self.user_city = None
        my_kwargs = {}

        for key, value in kwargs.items():
            if key == 'user_city':
                self.user_city = value
            else:
                my_kwargs[key] = value

        super().__init__(*kargs, **my_kwargs)

    def custom_init(self):
        """ custom init """
        self.fields['country'], self.fields['subject'], self.fields['city'] = \
            populate_country_subject_city(
                self.fields['country'],
                self.fields['subject'],
                self.fields['city'],
                self.user_city,
            )
