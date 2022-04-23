"""
template tags ifvar
"""
from django.template import Node, Variable, TemplateSyntaxError, Library


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

        if var in varlist:
            return self.outstr
        return ''


@register.tag()
def ifvar(parser, token):
    """
    {% isvar <var> in <varlist> <var or srting for return>%}
    if <var> is in <varlist> return <var or srting for return> else nothing
    """
    bits = token.split_contents()
    if len(bits) != 5:
        raise TemplateSyntaxError(
            "'%s' takes four arguments"
            " (isvar var in varlist)" % bits[0])

    if bits[2] != 'in':
        raise TemplateSyntaxError(
            "'%s' no takes argument %s for second parameter. Use parameter 'in'."
            " (isvar var in varlist)" % (bits[0], bits[2]))

    return IsVarNode(bits[1], bits[3], bits[4])
