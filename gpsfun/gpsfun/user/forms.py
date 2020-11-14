# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from gpsfun.DjHDGutils.newforms import TemplatedForm
#from olwidget.widgets import EditableMap

from gpsfun.main.GeoName.models import populate_country_subject_city
from gpsfun.main.GeoName.models import GeoCountry, GeoCountryAdminSubject, \
     country_iso_by_iso3, geocountry_by_code

from django.template.loader import render_to_string
from location_field.forms.plain import PlainLocationField
#from registration.forms import RegistrationFormUniqueEmail  #, attrs_dict


class CityForm(TemplatedForm):
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

        super(CityForm, self).__init__(*kargs, **my_kwargs)

    def custom_init(self):
        self.fields['country'], self.fields['subject'], self.fields['city'] = \
            populate_country_subject_city(
                self.fields['country'],
                self.fields['subject'],
                self.fields['city'],
                self.user_city,
            )

#class LocationForm(TemplatedForm):
    #location = forms.CharField(widget=EditableMap(options={'default_lat': 49.5800781249997, 'default_lon': 36.1405547824504, 'default_zoom': 11,},
                                                  #))
    #lat_deg = forms.CharField(widget=forms.TextInput(attrs={'size': '2', 'maxlength': '2',}),)
    #lat_min = forms.CharField(widget=forms.TextInput(attrs={'size': '2', 'maxlength': '2',}),)
    #lat_mindec = forms.CharField(widget=forms.TextInput(attrs={'size': '3', 'maxlength': '3',}),)
    #lon_deg = forms.CharField(widget=forms.TextInput(attrs={'size': '2', 'maxlength': '2',}),)
    #lon_min = forms.CharField(widget=forms.TextInput(attrs={'size': '2', 'maxlength': '2',}),)
    #lon_mindec = forms.CharField(widget=forms.TextInput(attrs={'size': '3', 'maxlength': '3',}),)

#class RegistrationGpsfunUser(RegistrationFormUniqueEmail):
    #username = forms.RegexField(regex=u'^[\u0400-\u0500\ \w\d\.\@\+\-]+$',
                                #max_length=30,
                                #widget=forms.TextInput(),
                                #label=_("Username"),
                                #error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})

#
