from copy import deepcopy
from urllib import urlencode,quote,unquote
from django.utils.datastructures import SortedDict
from django.http import Http404,HttpResponse,HttpResponseRedirect,HttpResponseForbidden
from DjHDGutils.paginator import Paginator
from DjHDGutils.datatable.column import Column
from DjHDGutils.datatable.options import Options,Source
from django.template.loader import render_to_string
#from DjHDGutils.datatable.datasource import DataSource
import types

def get_declared_columns(bases, attrs):
    columns = [(column_name, attrs.pop(column_name)) for column_name, obj in attrs.items() if isinstance(obj, Column)]
    columns.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

    for base in bases[::-1]:
        if hasattr(base, 'base_columns'):
            columns = base.base_columns.items() + columns

    return SortedDict(columns)

class ControllerBase(type):
    def __new__(cls, name, bases, attrs):
        columns = get_declared_columns(bases, attrs)
        for col in columns:
            columns[col].name = col
        attrs['base_columns'] = columns

        new_class = type.__new__(cls, name, bases, attrs)

        new_class.add_to_class('_meta', Options(attrs.pop('Meta', None)))

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)        

        return new_class

    def add_to_class(cls, name, value):
        if name == 'Source':
            assert type(value) == types.ClassType, "%r attribute of %s model must be a class, not a %s object" % (name, cls.__name__, type(value))
            value = Source(**dict([(k, v) for k, v in value.__dict__.items() if not k.startswith('_')]))

        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)        


class State(object):
    def __init__(self,controller,get_dict):
        self.contoller = controller
        self.state_changed = False
        self.default = True
        self.order_by = controller._meta.ordering

        self._pack_data = None

        if get_dict.get('state',None):
            self.default = False
            self.unpack(get_dict['state'])
            del get_dict['state']

        if get_dict.has_key('order_by'):
            #FIXME check before assign, if column may change ordering
            self.order_by = [get_dict['order_by'],]
            self.state_changed = True
            self.default = False
            del get_dict['order_by']
                

    def unpack(self,state_key):
        state = unquote(state_key)
        state = state.decode('base64_codec')
        lines = state.splitlines()
        if len(lines) > 0:
            self._unpack_order(lines[0])


    def is_changed(self):
        return self.state_changed
        
    def is_default(self):
        return self.default

    def _unpack_order(self,line):
        #FIXME check before assign, if column may change ordering
        self.order_by = line.split(',')

    def _pack_order(self):
        return ",".join(self.order_by)

    def pack(self):
        if self._pack_data:
            return self._pack_data

        self._pack_data = u""
        self._pack_data = self._pack_order()
        self._pack_data += u"\n"

#        print "----------------------"
        self._pack_data = "".join(self._pack_data.encode('base64_codec').splitlines())
#        print self._pack_data
        self._pack_data = 'state=%s'%(quote(self._pack_data))

#        print self._pack_data
        return self._pack_data





class Controller(object):
    __metaclass__ = ControllerBase

    def __init__(self,request):
        self.data_source = None
        self.columns = deepcopy(self.base_columns)
        self.request = request
        self.get_dict = request.GET.copy()
        
        self.state = State(self,self.get_dict)

        self._set_column_order_state()

    def get_column(self,colname):
        return self.columns.get(colname,None)

    def _set_column_order_state(self):
        # set ordering info for columns
        # currently this info used only in template to display order info
        for colname in self.state.order_by:
            desc = False
            if colname[0] == '-':
                colname = colname[1:]
                desc = True
            col = self.get_column(colname)

            if col:
                col.ordered_asc = not desc
                col.ordered_desc = desc

            # IMHO make sence to display order mode only for fist column
            break
                

    def get_redirect(self):
        if self.state.is_changed():
            return HttpResponseRedirect(self.get_start_url())

    def get_data_source(self):
        if self.data_source is None:
            self.data_source = self._meta.data_source.get_source()

        return self.data_source

    def resolve_column_data(self,column,row):
        return self.get_data_source().resolve_column_data(column,row)

    def iter_columns(self):
        for col in self.base_columns:
            yield self.columns[col]

    def get_start_url(self):
        url = '?'
        if len(self.get_dict.items()) > 0:
            url +=  self.get_dict.urlencode()
            url += '&'

        if not self.state.is_default():
            url += self.state.pack()
            url += '&'
            
        return url


    def as_html(self):
        ds = self.get_data_source()
        ds.set_ordering(self.state.order_by)
        
        return render_to_string('datatable.html',
                                { 'controller': self,
                                  'paginator': Paginator(ds,
                                                         self.request.GET.get('page',1),
                                                         self._meta.list_per_page,
                                                         request=self.request) })
    

