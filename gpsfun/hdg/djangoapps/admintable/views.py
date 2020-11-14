from django.views.generic.simple import direct_to_template
import datetime
from django import forms
from django.http import HttpResponseRedirect

def quicksearch_form(request, table):
    fields_to_search_on = []
    for field in table.settings.search_rules:
        if field[3].find('%s')!=-1:
            fields_to_search_on.append((field[1], table.verboose_column_name(field[1])))
    params={'title': 'Quick Search',
            'fields_to_search_on': fields_to_search_on,
            'table': table}

    return direct_to_template(request,
                              'AdminTable/quicksearch_form.html', params)



def search_form(request, table):
    params = dict(table=table,
                  today = datetime.date.today().isoformat(),
                  lastmonth = (datetime.date.today()\
                               -datetime.timedelta(days=31)).isoformat(), 
                  lastweek = (datetime.date.today()\
                              -datetime.timedelta(days=7)).isoformat(),
                  lastyear = (datetime.date.today()\
                              -datetime.timedelta(days=365)).isoformat(),
                  title = "Manage Filters")
    return direct_to_template(request,
                              'AdminTable/search_form.html', params)

def preferences_form(request, table):

    class PreferencesForm(forms.Form):
        shown_columns = forms.MultipleChoiceField(choices=table.columns(),
                                                  initial=[c for c,d \
                                                           in table.shown_columns()])
        rows_per_page = forms.IntegerField(initial=table.rows_per_page)
        current_page = forms.IntegerField(initial=table.current_page)
        sort_on = forms.ChoiceField(table.sortable_columns, initial=table.settings.sort_on)
        reverse_sort = forms.BooleanField(initial=table.settings.sort_reverse, required=False)

    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            table.set_shown_columns(form.cleaned_data['shown_columns'])
            table.set_rows_per_page(form.cleaned_data['rows_per_page'])
            table.set_current_page(form.cleaned_data['current_page'])
            table.set_sort_on(form.cleaned_data['sort_on'])
            table.set_sort_reverse(form.cleaned_data['reverse_sort'])
            return HttpResponseRedirect('?'+table.getvars())
    else:
        form = PreferencesForm()


    return direct_to_template(request,
                              'AdminTable/preferences_form.html',
                              dict(table = table,
                                   form = form,
                                   title = "Preferences"))

