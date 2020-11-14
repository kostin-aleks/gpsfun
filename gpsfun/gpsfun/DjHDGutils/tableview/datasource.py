


class BaseDatasource(object):
    def set_order(self, order_ref, asc):
        pass

    def set_limit(self, start, offset):
        pass

    def count(self):
        pass


class SqlDataSource(BaseDatasource):
    def __init__(self, sql):
        self.sql = sql

class QSDataSource(BaseDatasource):
    def __init__(self, qs):
        self.qs = qs

    def __iter__(self):
        return iter(self.qs)

    def __item__(self, key):
        pass

    def set_order(self, order_ref, asc):
        if asc:
            self.qs = self.qs.order_by(order_ref)
        else:
            self.qs = self.qs.order_by('-%s'%order_ref)

    def set_limit(self, start, offset):
        self.qs = self.qs[start:offset]

    def count(self):
        return self.qs.count()
            

    def filter(self, *kargs, **kwargs):
        self.qs = self.qs.filter(*kargs, **kwargs)

        return self

    def exclude(self, *kargs, **kwargs):
        self.qs = self.qs.exclude(*kargs, **kwargs)

        return self
        
