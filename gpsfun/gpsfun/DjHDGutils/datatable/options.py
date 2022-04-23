"""
options
"""
from DjHDGutils.datatable.datasource import QuertsetSource, SQLSource


DEFAULT_NAMES = ('list_per_page', 'ordering')


class Options(object):
    """ Options """

    def __init__(self, meta):
        self.data_source = None
        self.meta = meta
        self.list_per_page = None
        self.ordering = []

    def contribute_to_class(self, cls, name):
        """ contribute to class """
        cls._meta = self

        for key, value in cls.base_columns.iteritems():
            if not value.is_sortable:
                continue
            col = value.field or key
            self.ordering.append(col)

        if self.meta:
            meta_attrs = self.meta.__dict__
            del meta_attrs['__module__']
            del meta_attrs['__doc__']
            for attr_name in DEFAULT_NAMES:
                setattr(
                    self, attr_name,
                    meta_attrs.pop(attr_name, getattr(self, attr_name)))

        del self.meta


class Source(object):
    """ Source """

    def __init__(self, query=None, sql_from=None, sql_where=None):
        self.query = query
        self.sql_from = sql_from
        self.sql_where = sql_where or []

    def contribute_to_class(self, cls, name):
        """ contribute to class """
        cls._meta.data_source = self

        self.controller = cls

    def get_source(self):
        """ get source """
        if self.query is not None:
            return QuertsetSource(self.query._clone())
        else:
            return SQLSource(self.sql_from, self.sql_where)
