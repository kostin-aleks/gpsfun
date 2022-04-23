"""
database datasource
"""
from django.conf import settings


class DataSource(object):
    """ DataSource """

    def get_count(self):
        """ get count """
        pass

    def __iter__(self):
        pass

    def resolve_data(self, column, row):
        """ resolve data """
        return None

    def count(self):
        """ count """
        return None

    def __getitem__(self, k):
        return None

    def set_ordering(self, ordering):
        """ set ordering """
        pass


class QuertsetSource(DataSource):
    """ QuertsetSource """

    def __init__(self, qset):
        self.qset = qset._clone()

    def set_ordering(self, ordering):
        """ set ordering """
        self.qset = self.qset.order_by(*ordering)

    def count(self):
        """ count """
        return self.qset.count()

    def __getitem__(self, k):
        return self.qset[k]

    def resolve_column_data(self, column, row):
        """ resolve column data """
        field_name = column.field or column.name

        obj = row
        for item in field_name.split('.'):
            if hasattr(obj, item):
                obj = getattr(obj, item)
                if callable(obj):
                    try:
                        obj = obj()
                    except:
                        obj = settings.TEMPLATE_STRING_IF_INVALID
                        break

            else:
                obj = settings.TEMPLATE_STRING_IF_INVALID
                break

        return obj


class SQLSource(DataSource):
    """ SQLSource """

    def __init__(self, sql_from, sql_where):
        self.sql_from = sql_from
        self.sql_where = sql_where
