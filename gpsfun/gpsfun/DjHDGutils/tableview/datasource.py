"""
data source
"""


class BaseDatasource(object):
    """ BaseDatasource """

    def set_order(self, order_ref, asc):
        """ set order """
        pass

    def set_limit(self, start, offset):
        """ set limit """
        pass

    def count(self):
        """ count """
        pass


class SqlDataSource(BaseDatasource):
    """ SqlDataSource """

    def __init__(self, sql):
        self.sql = sql


class QSDataSource(BaseDatasource):
    """ QSDataSource """

    def __init__(self, qs):
        self.qs = qs

    def __iter__(self):
        return iter(self.qs)

    def __item__(self, key):
        pass

    def set_order(self, order_ref, asc):
        """ set order """
        if asc:
            self.qs = self.qs.order_by(order_ref)
        else:
            self.qs = self.qs.order_by('-%s' % order_ref)

    def set_limit(self, start, offset):
        """ set limit """
        self.qs = self.qs[start:offset]

    def count(self):
        """ count """
        return self.qs.count()

    def filter(self, *kargs, **kwargs):
        """ filter """
        self.qs = self.qs.filter(*kargs, **kwargs)

        return self

    def exclude(self, *kargs, **kwargs):
        """ exclude """
        self.qs = self.qs.exclude(*kargs, **kwargs)

        return self
