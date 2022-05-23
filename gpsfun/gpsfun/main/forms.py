"""
forms
"""
from django import forms
from django.template import Context, loader


__all__ = ['RequestModelForm', 'RequestForm']


class _Form:
    """ Form """

    def __init__(self, *kargs, **kwargs):
        """
        Init accept two additional arguments:
        request - http request from view
        template - optional template name


        Inherit class can define function init
        which will be called after complete __init__

        """
        self._request = None
        self._template = None
        self.kwargs = {}

        my_kwargs = {}

        # hack with iterators, because deepcopy not workin on production server
        for key, value in kwargs.items():
            if key == 'request':
                self._request = value
            elif key == 'template':
                self._template = value
            elif key == 'kwargs':
                self.kwargs = value
            else:
                my_kwargs[key] = value

        super(self._ref_class, self).__init__(*kargs, **my_kwargs)

        if hasattr(self, 'init'):
            init = getattr(self, 'init')
            if callable(init):
                init()

    def get_value_for(self, field_name):
        """
        used to obtain value of fields
        useful when need get value not depend on form state
        """
        if self.is_bound:
            return self[field_name].data
        return self.initial.get(field_name, self.fields[field_name].initial)

    def get_template_name(self):
        """ get template name """
        return self._template or "forms/form.html"

    def output_via_template(self):
        """
        Helper function for fieldsting fields data from form.
        """

        bound_fields = [forms.forms.BoundField(self, field, name)
                        for name, field
                        in self.fields.items()]

        c = Context(dict(form=self, bound_fields=bound_fields))
        t = loader.get_template(self.get_template_name())
        return t.render(c)

    def as_template(self):
        """ {{ form.as_template }} """
        for field in self.fields.keys():
            self.fields[field].str_class = str(self.fields[field].widget.__class__.__name__)
        return self.output_via_template()

    def set_model_fields(self, instance, exclude_fields=[]):
        """
        Fills values from the form fields into instance fields
        """
        data = self.cleaned_data
        for key in data:
            if key in instance._meta.get_all_field_names() and key not in exclude_fields:
                setattr(instance, f'{key}', data[key])

    def set_initial(self, instance):
        """ set initial """
        for field in self.fields.keys():
            if field in self.initial:
                continue
            if hasattr(instance, f'{field}'):
                attr = getattr(instance, f'{field}')
                if callable(attr):
                    attr = attr()
                self.initial[field] = attr


class RequestModelForm(_Form, forms.ModelForm):
    """ RequestModelForm """
    _ref_class = forms.ModelForm


class RequestForm(_Form, forms.Form):
    """ RequestForm """
    _ref_class = forms.Form


class RequestFormSet(forms.formsets.BaseFormSet):
    """ RequestFormSet """

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        self.form_args = kwargs.pop('args', [])

        super(RequestFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix(i),
            'error_class': self.error_class,
        }
        if self.is_bound:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial and 'initial' not in kwargs:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        defaults['request'] = self._request

        form = self.form(*self.form_args, **defaults)
        self.add_fields(form, i)
        return form

    @property
    def empty_form(self):
        """
        empty form
        """
        form = self.form(
            *self.form_args,
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
            request=self._request)
        self.add_fields(form, None)

        return form
