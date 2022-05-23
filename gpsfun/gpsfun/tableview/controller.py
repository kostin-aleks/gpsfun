"""
table controller
"""

from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import RequestContext
from gpsfun.main.db_utils import get_object_or_none

from .models import TableViewProfile
from .table import CellTitle, BoundRow
import pickle


class TableController:
    """ table controller """

    def __init__(self, table, datasource, request, row_per_page=None):
        self.table = table
        self.request = request
        self.profile = None
        self.filter_modified = False
        self.session_key = f"tableview_{self.table.id}"
        self.last_profile_key = f"{self.session_key}__last"
        self.source = datasource
        self.paginator = None
        self.visible_columns = []
        self.sort_by = []
        self.sort_asc = True
        self.filter = {}
        self.form_filter_instance = None
        self.search_value = None
        self.allow_manage_profiles = True

        if row_per_page:
            self._init_paginator(row_per_page)

    def _init_paginator(self, row_per_page):
        """ init paginator """
        self.paginator = Paginator(self.source,
                                   page=1,
                                   row_per_page=row_per_page,
                                   request=self.request)

    def show_column(self, column_name):
        """ show column """
        if column_name not in self.table.columns:
            return False

        if column_name in self.visible_columns:
            return False

        self.visible_columns.append(column_name)
        return True

    def get_paginated_rows(self):
        """ get paginated rows """
        if self.paginator:
            self.source.set_limit(*self.paginator.get_offset())

        row_index = 0
        for row in self.source:
            row_index += 1
            yield BoundRow(self, row_index, row)

    def set_page(self, page):
        """ set page """
        if self.paginator:
            self.paginator.page = page

    def set_sort(self, column_name):
        """ set sort """
        asc = True
        if column_name.startswith('-'):
            asc = False
            column_name = column_name[1:]

        if column_name in self.table.columns and column_name in self.table.sortable:
            self.sort_by = column_name
            self.sort_asc = asc

            column = self.table.columns[column_name]
            if hasattr(self.table, f'order_by_{column_name}'):
                order_callback = getattr(
                    self.table, f'order_by_{column_name}')
                order_callback(column, self.source, asc)
            else:
                self.source.set_order(column.refname, asc)
            return True

        return False

    def get_sort(self):
        """ get sort """
        if not self.sort_by:
            return ''
        if self.sort_asc:
            mode = ''
        else:
            mode = '-'

        return f"{mode}{self.sort_by}"

    def apply_state(self, state):
        """ apply state """
        self.visible_columns = state.get('visible', [])
        self.sort_by = state.get('sort_by')
        self.filter = state.get('filter', {}) or {}
        if self.sort_by:
            self.set_sort(self.sort_by)

    def get_state(self):
        """ get state """
        return {'visible': self.visible_columns,
                'sort_by': self.get_sort(),
                'filter': self.filter}

    def apply_search(self, value):
        """ apply search """
        self.search_value = value

    def restore(self, id=None):
        """ restore """
        state = None

        if id is None and self.last_profile_key in self.request.session:
            id = self.request.session[self.last_profile_key]
        elif id:
            self.request.session[self.last_profile_key] = id

        profile_qs = TableViewProfile.objects.filter(
            tableview_name=self.table.id)
        if self.table.global_profile:
            profile_qs = profile_qs.filter(user__isnull=True)
        else:
            profile_qs = profile_qs.filter(user=self.request.user)

        if (id is None and self.session_key not in self.request.session) or id == 'default':
            # load default state
            self.profile = get_object_or_none(profile_qs,
                                              is_default=True)

        elif id and id.isdigit():
            self.profile = get_object_or_none(
                profile_qs,
                is_default=False,
                pk=id)

        if self.session_key in self.request.session:
            state = self.request.session[self.session_key]

        if self.profile:
            state = self.profile.state

        if state:
            self.apply_state(state)

    def save(self):
        """ save """
        self.request.session[f"tableview_{self.table.id}"] = self.get_state()

    def save_state(self, name=None):
        """ save state """
        state = self.get_state()
        dump = pickle.dumps(state, pickle.HIGHEST_PROTOCOL)
        dump = dump.encode('hex_codec')

        kwargs = {'tableview_name': self.table.id,
                  'defaults': {'dump': dump},
                  }
        if self.table.global_profile:
            kwargs['user__isnull'] = True
        else:
            kwargs['user'] = self.request.user

        if name is None:
            kwargs['is_default'] = True
        else:
            kwargs['is_default'] = False
            kwargs['label'] = name

        profile, created = TableViewProfile.objects.get_or_create(**kwargs)

        if not created:
            profile.dump = dump
            profile.save()

        return {'status': 'OK',
                'id': profile.id,
                'created': created}

    def remove_profile(self, profile_id):
        """ remove profile """
        qs = TableViewProfile.objects.filter(
            id=profile_id,
            tableview_name=self.table.id,
            is_default=False
        )
        if self.table.global_profile:
            qs = qs.filter(user__isnull=True)
        else:
            qs = qs.filter(user=self.request.user)

        qs.delete()
        return {'status': 'OK'}

    def process_request(self):
        """ process request """
        self.restore(self.request.GET.get('profile'))

        if 'page' in self.request.GET:
            self.set_page(self.request.GET.get('page'))

        if self.request.is_ajax():
            if self.request.GET.get('action') == 'save_state':
                return self.save_state()

            if self.request.GET.get('action') == 'save_state_as':
                return self.save_state(self.request.GET.get('name'))

            if self.request.GET.get('action') == 'load_json':
                fun_name = f"ajax_{self.request.GET.get('function', 'undef')}"
                if hasattr(self.table, fun_name):
                    fun = getattr(self.table, fun_name)
                    if callable(fun):
                        return fun(self.request)

            if self.request.GET.get('action') == 'remove_profile':
                return self.remove_profile(self.request.GET.get('value'))

            if self.request.GET.get('action') == 'load_page':
                return {'page_count': self.paginator.get_page_count(),
                        'body': render_to_string(
                            "table_body_content.html",
                            RequestContext(
                                self.request,
                                {'table': self.table,
                                 'controller': self,
                                 })),
                        'paginator': render_to_string(
                            "table_paginator.html",
                            RequestContext(
                                self.request,
                                {'table': self.table,
                                 'controller': self,
                                 })),
                        }

        if 'search' in self.request.GET:
            self.apply_search(self.request.GET['search'])

        result = self.process_form_filter()

        if 'sort_by' in self.request.GET:
            self.set_sort(self.request.GET.get('sort_by'))
            result = HttpResponseRedirect('?profile=custom')

        if self.request.method == 'POST':
            if '_save_column_setup' in self.request.POST:
                prefix = f"setup_{self.table.id}_column_"
                self.visible_columns = []
                for key, value in self.request.POST.iteritems():
                    if key.startswith(prefix):
                        self.show_column(value)
                result = HttpResponseRedirect("?profile=custom")

        self.save()

        return result if result else None

    def process_form_filter(self):
        """ process form filter """
        if not self.table.filter_form:
            return

        if self.request.method == 'POST' and 'form_filter' in self.request.POST:
            form = self.table.filter_form(
                self.request.POST, request=self.request)
            if form.is_valid():
                self.filter = form.cleaned_data

                self.save()
                return HttpResponseRedirect("?profile=custom")
        else:
            form = self.table.filter_form(request=self.request,
                                          initial=self.filter)
        self.form_filter_instance = form
        return None

    def get_saved_state(self):
        """ get saved state """
        if self.table.global_profile:
            return TableViewProfile.objects.filter(user__isnull=True,
                                                   tableview_name=self.table.id,
                                                   is_default=False)
        else:
            return TableViewProfile.objects.filter(user=self.request.user,
                                                   tableview_name=self.table.id,
                                                   is_default=False)

    def iter_columns(self):
        """ iter columns """
        for key, column in self.table.columns.iteritems():
            if key in self.table.permanent or key in self.visible_columns:
                yield (key, column)

    def iter_all_columns(self):
        """ iter all columns """
        for key, column in self.table.columns.iteritems():
            yield (key, column)

    def iter_all_title(self):
        """ iter all title """
        for key, column in self.iter_all_columns():
            yield (key, CellTitle(self, key, column))

    def iter_title(self):
        """ iter title """
        for key, column in self.iter_columns():
            yield (key, CellTitle(self, key, column))

    def as_html(self):
        """ as html """
        if self.search_value:
            self.table.apply_search(self.search_value, self.source)
        else:
            self.table.apply_filter(self.filter, self.source)

        if self.paginator:
            self.paginator._calc()

        return render_to_string(
            "table_body.html",
            RequestContext(
                self.request,
                {'table': self.table,
                 'filter_form': self.form_filter_instance,
                 'controller': self,
                 'base_count': (self.paginator.page - 1) * self.paginator.row_per_page,
                 }))
