from django.conf import settings


class DataSource(object):


    def get_count(self):
        pass

    def __iter__(self):
        pass

    def resolve_data(self,column,row):
        return None

    def count(self):
        return None

    def __getitem__(self,k):
        return None

    def set_ordering(self,ordering):
        pass

class QuertsetSource(DataSource):

    def __init__(self,qset):
        self.qset = qset._clone()

    def set_ordering(self,ordering):
        self.qset = self.qset.order_by(*ordering)

    def count(self):
        return self.qset.count()

    def __getitem__(self,k):
        return self.qset[k]
            
    def resolve_column_data(self,column,row):
        field_name = column.field or column.name

        obj = row
        for item in field_name.split('.'):
            if hasattr(obj,item):
                obj = getattr(obj,item)
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
    def __init__(self,sql_from,sql_where):
        self.sql_from = sql_from
        self.sql_where = sql_where
    

