# basic idea from http://code.activestate.com/recipes/496923/
# provided by Alex Greif
#
import string
import xml
if hasattr(xml, "use_pyxml"):
    xml.use_pyxml()

from xml.marshal import generic


class Marshaller(generic.Marshaller):
    tag_unicode = 'unicode'
    tag_boolean = 'boolean'

    def m_unicode(self, value, dict):
        name = self.tag_unicode
        L = ['<' + name + '>']
        s = value.encode('utf-8')
        if '&' in s or '>' in s or '<' in s:
            s = s.replace('&', '&amp;')
            s = s.replace('<', '&lt;')
            s = s.replace('>', '&gt;')
        L.append(s)
        L.append('</' + name + '>')
        return L

    def m_bool(self, value, dict):
        name = self.tag_boolean
        L = ['<' + name + '>']
        L.append(value and 'True' or 'False')
        L.append('</' + name + '>')
        return L
        


class Unmarshaller(generic.Unmarshaller):
    def __init__(self):
        self.unmarshal_meth['unicode'] = ('um_start_unicode','um_end_unicode')
        self.unmarshal_meth['boolean'] = ('um_start_boolean','um_end_boolean')
        # super maps the method names to methods
        generic.Unmarshaller.__init__(self)

    um_start_unicode = generic.Unmarshaller.um_start_generic
    um_start_boolean = generic.Unmarshaller.um_start_generic

    def um_end_unicode(self, name):
        ds = self.data_stack
        # the value is a utf-8 encoded unicode
        ds[-1] = ''.join(ds[-1])
        self.accumulating_chars = 0

    def um_end_boolean(self, name):
        ds = self.data_stack
        ds[-1] = string.join(ds[-1], "")
        ds[-1] = (ds[-1]=='True')
        self.accumulating_chars = 0

