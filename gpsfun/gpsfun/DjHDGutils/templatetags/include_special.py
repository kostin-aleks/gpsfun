"""
template tags include special
"""
from django import template
from django.template.loader import render_to_string

register = template.Library()


class CallTemplate(template.Node):
    def __init__(self, args):
        self._args = args

    def render(self, context):
        template_name = template.Variable(self._args[0]).resolve(context)
        args_iter = self._args[1:].__iter__()
        while True:
            try:
                name = template.Variable(args_iter.next()).resolve(context)
                value = template.Variable(args_iter.next()).resolve(context)
                context[name] = value
            except StopIteration:
                break
        return render_to_string(template_name, context)


def include_arg(parser, token):
    """ this tag allows to include requested template passing specific arguments """
    args = token.split_contents()
    return CallTemplate(args[1:])


register.tag(include_arg)
