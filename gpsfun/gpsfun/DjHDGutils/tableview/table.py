"""
table
"""
from copy import deepcopy
import csv
from django.utils.datastructures import SortedDict
from django.db.models import Q

from DjHDGutils.tableview import widgets


def get_declared_fields(bases, attrs, with_base_columns=True):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases'). This is used by both the
    Form and ModelForm metclasses.

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in ModelForm subclassing.
    Also integrates any additional media definitions
    """
    columns = [(column_name, attrs.pop(column_name))
               for column_name, obj in attrs.items()
               if isinstance(obj, widgets.BaseWidget)]
    columns.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_columns:
        for base in bases[::-1]:
            if hasattr(base, 'base_columns'):
                columns = base.base_columns.items() + columns
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_columns'):
                columns = base.declared_columns.items() + columns

    return SortedDict(columns)


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_columns'] = get_declared_fields(bases, attrs)

        attr_meta = attrs.pop('Meta', None)

        permanent = ()
        sortable = ()
        filter_form = None
        search = ()
        use_keyboard = False
        global_profile = False
        template = "table_body.html"
        reload_interval = None
        csv_allow = False
        csv_dialect = csv.excel

        if attr_meta:
            permanent = getattr(attr_meta, 'permanent', ())
            sortable = getattr(attr_meta, 'sortable', ())
            filter_form = getattr(attr_meta, 'filter_form', None)
            search = getattr(attr_meta, 'search', None)
            use_keyboard = getattr(attr_meta, 'use_keyboard', False)
            reload_interval = getattr(attr_meta, 'reload_interval', None)
            global_profile = getattr(attr_meta, 'global_profile', False)
            template = getattr(attr_meta, 'template', "table_body.html")
            csv_allow = getattr(attr_meta, 'csv_allow', False)
            csv_dialect = getattr(attr_meta, 'csv_dialect', csv.excel)

        attrs['permanent'] = permanent
        attrs['sortable'] = sortable
        attrs['filter_form'] = filter_form
        attrs['search'] = search
        attrs['use_keyboard'] = use_keyboard
        attrs['global_profile'] = global_profile
        attrs['template'] = template
        attrs['reload_interval'] = reload_interval
        attrs['csv_allow'] = csv_allow
        attrs['csv_dialect'] = csv_dialect

        new_class = super(DeclarativeFieldsMetaclass, cls).__new__(cls, name, bases, attrs)

        return new_class


class BaseTableView(object):
    def __init__(self, ref_id, **kwargs):
        self.columns = deepcopy(self.base_columns)
        self.id = ref_id
        self.kwargs = kwargs

    def get_id(self):
        """ get id """
        return self.id

    def get_row_class(self, row):
        """ get row class """
        return ''

    def apply_filter(self, filter, source):
        """ apply filter """
        pass

    def apply_search(self, search_value, source):
        """ apply search """
        if not search_value:
            return
        search_filter = []
        for orm_field_name in self.search:
            filter_name = f"{orm_field_name}__icontains"
            search_filter.append(Q(**{filter_name: search_value}))

        if search_filter:
            result_q = Q()
            for item in search_filter:
                result_q.add(item, Q.OR)
            source.filter(result_q)


class CellTitle(object):
    """ CellTitle """

    def __init__(self, controller, key, column):
        self.controller = controller
        self.key = key
        self.column = column

    def is_sortable(self):
        """ is sortable ? """
        return self.key in self.controller.table.sortable

    def is_sorted(self):
        """ is sorted ? """
        return self.key == self.controller.sort_by

    def is_asc(self):
        """ is asc ? """
        return self.key == self.controller.sort_by and self.controller.sort_asc

    def html_title(self):
        """ html title """
        return self.column.html_title()

    def html_title_attr(self):
        """ html title attr """
        return self.column.html_title_attr()

    def is_permanent(self):
        """ is permanent ? """
        return self.key in self.controller.table.permanent

    def is_visible(self):
        """ is visible ? """
        return self.key in self.controller.visible_columns


class BoundCell(object):
    """ BoundCell """

    def __init__(self, row_index, key, bound_row, column):
        self.row_index = row_index
        self.bound_row = bound_row
        self.key = key
        self.column = column
        self.row_index = row_index

    def get_cell_class(self):
        """ get cell class """
        if hasattr(self.bound_row.controller.table, f'cell_class_{self.key}'):
            cb = getattr(self.bound_row.controller.table, f'cell_class_{self.key}')
            return cb(self.bound_row.controller.table, self.row_index, self.bound_row.row, self.column.get_value(self.bound_row.row))
        return ''

    def get_cell_style(self):
        """ get cell style """
        if hasattr(self.bound_row.controller.table, f'cell_style_{self.key}'):
            cb = getattr(self.bound_row.controller.table, f'cell_style_{self.key}')
            return cb(self.bound_row.controller.table, self.row_index, self.bound_row.row, self.column.get_value(self.bound_row.row))
        return ''

    def as_html(self):
        """ as html """
        if hasattr(self.bound_row.controller.table, f'render_{self.key}'):
            cb = getattr(self.bound_row.controller.table, f'render_{self.key}')
            return cb(self.bound_row.controller.table, self.row_index, self.bound_row.row, self.column.get_value(self.bound_row.row))

        return self.column.html_cell(self.row_index, self.bound_row.row)

    def html_cell_attr(self):
        """ html cell attributes """
        return self.column.html_cell_attr()

    def get_id(self):
        """ get id """
        return self.key


class BoundRow(object):
    """ BoundRow """

    def __init__(self, controller, row_index, row):
        self.controller = controller
        self.row = row
        self.row_index = row_index

    def __iter__(self):
        for key, column in self.controller.iter_columns():
            yield BoundCell(self.row_index, key, self, column)

    def get_id(self):
        """ get id """
        table_id = self.controller.table.get_id() or 'table'

        return f"{table_id}_row_{self.row_index}"

    def get_row_class(self):
        """ get row class """
        return self.controller.table.get_row_class(self.controller, self.row)


class TableView(BaseTableView):
    """ TableView """
    __metaclass__ = DeclarativeFieldsMetaclass
