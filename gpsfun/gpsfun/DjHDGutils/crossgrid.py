"""
CrossGrid reports



=================================================================================
 Report.title | Report.columns[].obj | Report.columns[].obj | .. |

=================================================================================
ReportRow.obj |  Column              | Column               | .. |
ReportRow.obj |  Column              | Column               | .. |
..................

ReportRow.obj |  Column              | Column               | .. |
================================================================================

"""

from django.utils.datastructures import SortedDict


class Column(object):
    """ Column """

    def __init__(self, report_row, key):
        self.key = key
        self.report_row = report_row
        self.value = None

    def append(self, obj):
        """ append """
        self.value = self.report_row.report.agg_function(obj, self.value)


class ReportRow(object):
    """ ReportRow """

    def __init__(self, report, obj, row_key):
        self.report = report
        self.columns = {}

        # will be used while rendering report as key object for row
        self.obj = obj
        if hasattr(self.obj, 'crossgrid_init'):
            _init = getattr(self.obj, 'crossgrid_init')
            if callable(_init):
                _init(self)

    def append(self, col_key, obj):
        """ append """
        col = self.columns.setdefault(col_key, Column(self, col_key))
        col.append(obj)

    def iter_columns(self):
        """ iterate columns """
        for col_key in self.report.columns.iterkeys():
            yield self.columns.get(col_key)

    def iter_headers_columns(self):
        """ iterate headers columns """
        for col_key in self.report.columns.iterkeys():
            yield self.report.columns.get(col_key), self.columns.get(col_key)


class CrossGridReport(object):
    """ CrossGridReport """

    def __init__(self,
                 title,
                 row_reduce,
                 row_map,
                 col_reduce,
                 agg_function,
                 header_map,
                 row_sort=None):
        """
        row_reduce:   reference to row reduce function
                      it take element and should return row key

        row_map:      function to map row basic object;
                      take 1 argument: object;
                      value, returned by this function will be used when
                      printing row

        col_reduce:   same as row_reduce but for columns

        agg_function: funciton will call when apped value to the column
                      for extract data from object;
                      take 2 arguments: object, current value

        header_map: function will call when adding new key into column header
                    take 1 argument: object

        """
        self.title = title
        self.row_reduce = row_reduce
        self.row_map = row_map
        self.col_reduce = col_reduce
        self.agg_function = agg_function
        self.header_map = header_map
        self.row_sort = row_sort

        self.row = SortedDict()
        self.columns = SortedDict()

    def append(self, obj):
        """ append """
        row_key = self.row_reduce(obj)
        col_key = self.col_reduce(obj)

        if col_key not in self.columns:
            self.columns[col_key] = self.header_map(obj)

        row_obj = self.row_map(obj)
        row = self.append_row(row_obj, row_key)
        row.append(col_key, obj)

    def append_row(self, row_obj, row_key):
        """ append row """
        return self.row.setdefault(row_key, ReportRow(self, row_obj, row_key))

    def append_column(self, col_obj, col_key):
        """ append column """
        self.columns.setdefault(col_key, col_obj)

    def iter_columns(self):
        """ iterate columns """
        return self.columns.itervalues()

    def iter_columns_key(self):
        """ iterate columns key """
        return self.columns.iterkeys()

    def iter_rows(self):
        """ iterate rows """
        return self.row.itervalues()
