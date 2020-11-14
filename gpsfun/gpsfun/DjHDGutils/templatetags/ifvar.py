#from django.conf import settings

#from django.template import NodeList, Template, Context
#from django.template import VariableDoesNotExist, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END
#from django.template import get_library, InvalidTemplateLibrary, resolve_variable

#from django.utils.encoding import smart_str, smart_unicode
#from django.utils.itercompat import groupby
#from django.utils.safestring import mark_safe

from django.template import Node, Variable, TemplateSyntaxError, Library
import types

register = Library()


class IsVarNode(Node):
    def __init__(self, var, varlist, outstr):
        self.var = Variable(var)
        self.varlist = Variable(varlist)
        if outstr[0] == outstr[-1] and outstr[0] in ('"', "'"):
            self.outstr = outstr[1:-1]
        else:
            self.outstr = Variable(outstr).resolve(context)

    def render(self, context):
        var = self.var.resolve(context)
        varlist = self.varlist.resolve(context)

#        if type(varlist) != types.ListType and type(varlist) != types.TupleType:
#            return ''
        
        if var in varlist:
            return self.outstr
        return ''


@register.tag()#(name="ifvar")
def ifvar(parser, token):
    '''
    {% isvar <var> in <varlist> <var or srting for return>%}
    if <var> is in <varlist> return <var or srting for return> else nothing
    '''
    bits = token.split_contents()
    if len(bits) != 5:
        raise TemplateSyntaxError("'%s' takes four arguments"
                                  " (isvar var in varlist)" % bits[0])

    if bits[2] != 'in':
        raise TemplateSyntaxError("'%s' no takes argument %s for second parameter. Use parameter 'in'."
                                  " (isvar var in varlist)" % (bits[0], bits[2]))

    var = parser.compile_filter(bits[1])
    varlist = bits[3]
    return IsVarNode(bits[1], bits[3], bits[4])
