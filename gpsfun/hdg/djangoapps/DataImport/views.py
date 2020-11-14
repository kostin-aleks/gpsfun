import csv

from django import forms
from django.urls import reverse
from django.db.models.loading import get_models, get_model
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from dateutil.parser import parse
from django.db import models
from django.views.generic.simple import direct_to_template
import tempfile
import os
from django.utils.encoding import force_unicode, smart_str

# "di" prefix means "data import"

# need use same from djhdgutils (when djhdgutils will be moved to hg)
def atoi(value, default=None):
    try:
        rc = int(value)
    except (ValueError, TypeError):
        rc = default
    return rc


#http://stackoverflow.com/questions/904041/reading-a-utf8-csv-file-with-python/904085#904085
def unicode_csv_reader(utf8_data):
    csv_reader = csv.reader(utf8_data)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


class UploadFileForm(forms.Form):
    file = forms.FileField(label=_('File'))

    def __init__(self, session, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.session = session


    def clean(self):
        if self.errors:
            return

        cleaned_data = self.cleaned_data

        file = cleaned_data.get('file')

        # remove old uploaded file
        old_file_name = self.session.get('di_file_name')
        if old_file_name:
            if os.path.exists(old_file_name):
                os.remove(old_file_name)

            del self.session['di_file_name']

        # save uploaded file to temporary file
        f = tempfile.NamedTemporaryFile(delete=False)

        for chunk in file.chunks():
            f.write(chunk)

        self.session['di_file_name_user'] = file.name
        self.session['di_file_name'] = f.name

        f.seek(0)
        csv_reader = unicode_csv_reader(f) #csv.reader(f)
        # read csv header
        first_row = csv_reader.next()
        if len(first_row) < 1:
            raise forms.ValidationError(_("Empty first row"))

        csv_fields = first_row

        self.session['di_csv_fields'] = csv_fields
        self.session['di_csv_file_name'] = file.name

        # reset field match
        d = {}
        d.update([(f, None) for f in csv_fields])
        self.session['di_field_match'] = d

        return cleaned_data



def upload_file(request):
    """ upload csv file """

    if request.method == 'POST':
        form = UploadFileForm(request.session, request.POST, request.FILES)
        if form.is_valid():
            activate_next_step(request.session)
            return HttpResponseRedirect(reverse('data-import'))
    else:
        form = UploadFileForm(request.session)

    return direct_to_template(request, 'DataImport/upload_file.html',
                              {'form': form,
                               'file': form['file'].errors,
                               'steps': DI_STEPS,
                               })



def get_appmodels():
    " return list of all application and model names: ['App1.Model1', ...] "

    r = [m._meta.app_label+'.'+m.__name__ for m in get_models()]
    r.sort()
    return r


# move method to form?
def render_field(form, field_name):
    field = form.fields[field_name]
    bound_field = forms.forms.BoundField(form, field, field_name)
    return bound_field.as_widget()


def xml_http_call_response(content=None):
    """ generate ajax server response expected by xmlhttplib.js

        content - dictionary of return parameters  """

    r = HttpResponse(simplejson.dumps(dict(content=content),
                                      ensure_ascii=False),
                     mimetype='application/javascript')
    return r


def get_appmodel_fields(appmodel):
    """ return list of application model field names """
    app, model = appmodel.split('.')
    model_class = get_model(app, model)
    return [f.name for f in model_class._meta.fields]


APPMODELS = get_appmodels()
DEFAULT_APPMODEL = APPMODELS[0]

class FieldChoiceForm(forms.Form):
    field_match = forms.ChoiceField(
        label='%s => model',
        required=False,
        widget=forms.Select(attrs=dict(size=20,
                                       name='field_match',
                                       )))

    appmodel = forms.ChoiceField(
        required=False,
        choices=[(am, am) for am in APPMODELS],
        initial=DEFAULT_APPMODEL,
        label='application.model',
        widget=forms.Select(attrs=dict(size=1)),
        )

    django_fields = forms.ChoiceField(
        required=False,
        choices=[(f, f) for f in get_appmodel_fields(DEFAULT_APPMODEL)],
        initial=get_appmodel_fields(DEFAULT_APPMODEL)[0],
        label='django fields for appmodel',
        widget=forms.Select(attrs=dict(size=20,
                                       name='django_fields',
                                       )),
        )

    action = forms.CharField(widget=forms.HiddenInput, required=False,
                             label="logical action of POST")



    def __init__(self, session, *args, **kwargs):
        super(FieldChoiceForm, self).__init__(*args, **kwargs)
        self.session = session

        self.refresh_django_fields_choices()
        self.refresh_field_match_choices()



        self.fields['field_match'].label = \
             '%s => %s' % (session.get('di_file_name_user'), 'database')


    def refresh_django_fields_choices(self):
        appmodel = self.session['di_choosed_appmodel']

        field_list = get_appmodel_fields(appmodel)

        c = [(f, f) for f in field_list]
        self.fields['django_fields'].choices = c
        if c:
            self.fields['django_fields'].initial = c[0][0]


    def refresh_field_match_choices(self):
        """ refresh form field_match choises according session data """

        csv_fields = self.session['di_csv_fields']
        fields_match = self.session['di_field_match']

        c = [(csv_f, '%s => %s' % (csv_f, fields_match[csv_f] or ''))
             for csv_f in csv_fields]

        self.fields['field_match'].choices = c
        if c:
            self.fields['field_match'].initial = c[0][0]


    def clean(self):
        cleaned_data = self.cleaned_data

        #file = cleaned_data.get('file')

        field_match = cleaned_data.get('field_match')
        appmodel = cleaned_data.get('appmodel')
        django_fields = cleaned_data.get('django_fields')
        action = cleaned_data.get('action')

        if action == 'set_appmodel':
            if not appmodel in get_appmodels():
                raise forms.ValidationError(_("Wrong appmodel"))

            self.session['di_choosed_appmodel'] = appmodel
            self.refresh_django_fields_choices()

            # reset field match values
            d = {}
            d.update([(f, None) for f in self.session['di_csv_fields']])
            self.session['di_field_match'] = d

            self.refresh_field_match_choices()

        elif action == 'set_field_match':
            if not field_match:
                raise forms.ValidationError(_("wrong field_match"))

            d = self.session['di_field_match']
            d[field_match] = '%s.%s' % (appmodel, django_fields)
            self.session['di_field_match'] = d

            self.refresh_field_match_choices()
        elif action == 'clear_field_match':
            if not field_match:
                raise forms.ValidationError(_("wrong field_match"))

            d = self.session['di_field_match']
            d[field_match] = None
            self.session['di_field_match'] = d

            self.refresh_field_match_choices()

        return cleaned_data


def format_form_errors(form):
    """ return form errors as readable text """

    errors_text = '\n'.join(['%s: %s' % (k,','.join(v))
                             for k, v in form.errors.iteritems()])

    errors_text = errors_text.replace('__all__: ', '')

    return errors_text


def field_choice(request):
    """ set correspondence between csv and model fields """

    session = request.session

    # default empty values
    if not session.has_key('di_csv_fields'):
        session['di_csv_fields'] = []
        session['di_field_match'] = {}

    if not session.has_key('di_choosed_appmodel'):
        session['di_choosed_appmodel'] = DEFAULT_APPMODEL

    if request.method == 'POST':
        form = FieldChoiceForm(session, request.POST, request.FILES)
        if form.is_valid():
            action = form.cleaned_data['action']

            # to rerender form with creaned_data
            form.data = form.cleaned_data

            if action == 'set_file':
                return xml_http_call_response(
                    dict(file_preview_html=render_field(form, 'file_preview'),
                         field_match_html=render_field(form, 'field_match'),
                         ))
            if action == 'set_appmodel':
                return xml_http_call_response(
                    dict(django_fields_html=render_field(form, 'django_fields'),
                         field_match_html=render_field(form, 'field_match'),
                         ))
            elif action in ['set_field_match', 'clear_field_match']:
                return xml_http_call_response(
                    dict(field_match_html=render_field(form, 'field_match'),
                         ))
            elif action == 'finish':
                activate_next_step(session)
                return HttpResponseRedirect(reverse('data-import'))
        else:
            return xml_http_call_response(
                dict(errors=format_form_errors(form)))

    else:
        form = FieldChoiceForm(session)

    r = direct_to_template(request, 'DataImport/field_choice.html',
                           {'form': form,
                            'steps': DI_STEPS,
                            #'file_name': session.get('di_file_name_user')
                           })

    return r


class ImportProcessForm(forms.Form):
    log = forms.CharField(required=False, label='Log',
                          initial='Please, wait...',
                          widget=forms.Textarea())

    action = forms.CharField(widget=forms.HiddenInput, required=False,
                             label="logical action of POST")

    def __init__(self, session, *args, **kwargs):
        super(ImportProcessForm, self).__init__(*args, **kwargs)
        self.session = session


    def clean(self):
        cleaned_data = self.cleaned_data
        action = cleaned_data.get('action')
        if action == 'import_data':
            try:
                f = open(self.session['di_file_name'])
            except IOError, e:
                raise forms.ValidationError(_("Cannot open file. Please, upload csv file again."))

            csv_reader = unicode_csv_reader(f) #csv.reader(f)

            field_match = self.session['di_field_match']

            if not any(field_match.values()):
                raise forms.ValidationError(_("Too little fields selected"))

            appmodel = next(am for am in field_match.values() if am)
            # (first non-empty appmodel - currently items has same appmodel)

            app_name, model_name = appmodel.split('.')[:2]

            model = get_model(app_name, model_name)

            csv_fields = self.session['di_csv_fields']

            model_fields_csv_order = [field_match[csv_f]
                                      for csv_f in csv_fields]

            log = ''

            try:
                first_row = True
                for row in csv_reader:
                    if first_row:
                        first_row = False
                        continue

                    #print row
                    params = [(str(n.split('.')[-1]), v)
                              for n, v in zip(model_fields_csv_order, row)
                              if n
                              ]

                    #
                    params = []
                    for n, v in zip(model_fields_csv_order, row):
                        if n:
                            param_name = str(n.split('.')[-1])

                            field_class = model._meta.get_field_by_name(param_name)[0].__class__

                            # parse datetime
                            if field_class in [models.DateField,
                                               models.DateTimeField]:
                                v = parse(v)

                            params.append((smart_str(param_name), unicode(v)))

                    format_params = ', '.join(['%s="%s"' % (n,v)
                                               for n,v in params])

                    log += '%s.%s.objects.create(%s) -> ' % (app_name,
                                                             model_name,
                                                             format_params)

                    try:
                        p = dict(params)
                        print p
                        if hasattr(model, '_csvimport'):
                            model._csvimport(**p)
                        else:
                            model.objects.create(**p)
                    except Exception, e:
                        log += 'Error' + '(%s)' % e.__class__ +':' + e.message
                    else:
                        log += 'OK'

                    log += '\n'

            except Exception, e:
                log += 'Error' + '(%s)' % e.__class__ +':' + e.message

            cleaned_data['log'] = log

        return cleaned_data



def import_process(request):
    """ do import and show import log """
    session = request.session

    if request.method == 'POST':
        form = ImportProcessForm(session, request.POST, request.FILES)
        if form.is_valid():
            action = form.cleaned_data['action']

            # to rerender form with creaned_data
            form.data = form.cleaned_data

            if action == 'import_data':
                return xml_http_call_response(
                    dict(log_html=render_field(form, 'log'),
                         ))

        else:
            return xml_http_call_response(
                dict(errors=format_form_errors(form)))
    else:
        form = ImportProcessForm(session)

    r = direct_to_template(request, 'DataImport/import_process.html',
                           {'form': form,
                            'steps': DI_STEPS,
                            })

    return r


# steps of data import
DI_STEPS = [dict(view=upload_file,
                 title=_('1. Upload csv file'),
                 url='?step=0',
                 enabled=True,
                 visible=True,
                 active=True,
                 ),
            dict(view=field_choice,
                 title=_('2. Set field match'),
                 url='?step=1',
                 enabled=False,
                 visible=False,
                 active=False,
                 ),
            dict(view=import_process,
                 title=_('3. Import'),
                 url='?step=2',
                 enabled=False,
                 visible=False,
                 active=False,
                 ),
            ]


def get_active_step_index():
    """ get index of active wizard step """
    return [i for i, s in enumerate(DI_STEPS) if s['active']][0]


def activate_step(session, step_index):
    """ activate wizard step. No validation performed

        Current realization: show pre-active steps, hide post-active steps.

    """
    for i, s in enumerate(DI_STEPS):
        if i < step_index:
            s['active'] = False
            s['visible'] = True
            s['enabled'] = True
        elif i == step_index:
            s['active'] = True
            s['visible'] = True
            s['enabled'] = True
        elif i > step_index:
            s['active'] = False
            s['visible'] = False
            #s['enabled']   (not changed)

    session['di_step'] = step_index


def activate_next_step(session):
    activate_step(session, get_active_step_index() + 1)



def data_import(request):
    """ step of data import """

    session = request.session

    available_steps = [i for i, s in enumerate(DI_STEPS) if s['enabled']]

    GET_step = atoi(request.GET.get('step'))

    if GET_step != None:
        if GET_step not in available_steps:
            # redirect to current step (session
            return HttpResponseRedirect(reverse('data-import'))
            #raise Http404('GET-step is not available')

        activate_step(session, GET_step)

    if not session.has_key('di_step'):
        activate_step(session, available_steps[0])

    di_step = atoi(session.get('di_step'))

    return DI_STEPS[di_step]['view'](request)









