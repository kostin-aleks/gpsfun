"""
template tags flatpage extensions
"""
from django import template
from django.template import Variable


register = template.Library()


class PrintColumnNode(template.Node):
    def __init__(self, column, row, controller):
        self.column = Variable(column)
        self.row = Variable(row)
        self.controller = Variable(controller)

    def render(self, context):
        try:
            column = self.column.resolve(context)
            row = self.row.resolve(context)
            controller = self.controller.resolve(context)
            col_data = controller.resolve_column_data(column, row)
            return column.print_column(col_data, controller)

        except template.VariableDoesNotExist:
            return ''


@register.tag()
def print_column(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, column, row, controller = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            f"{token.contents.split()[0]} tag requires exactly 3 arguments")

    return PrintColumnNode(column, row, controller)


class PrintHrefNode(template.Node):
    def __init__(self, column, row, controller):
        self.column = Variable(column)
        self.row = Variable(row)
        self.controller = Variable(controller)

    def render(self, context):
        try:
            column = self.column.resolve(context)
            controller = self.controller.resolve(context)
            row = self.row.resolve(context)
            fun_name = f"get_{column.name}_href"
            if hasattr(controller, fun_name):
                fnc = getattr(controller, fun_name)
                if callable(fnc):
                    rc = fnc(row)

                    if isinstance(rc, dict):
                        rc_str = ''
                        for key, value in rc.items():
                            rc_str += f"{key}='{value}'"
                        return rc_str

                    return f"href='{rc}'"

            return ""

        except template.VariableDoesNotExist:
            return ''


@register.tag()
def print_href(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, column, row, controller = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            f"{token.contents.split()[0]} tag requires exactly 3 arguments")

    return PrintHrefNode(column, row, controller)


class ColumnOrderNone(template.Node):
    def __init__(self, column, controller):
        self.column = Variable(column)
        self.controller = Variable(controller)

    def render(self, context):
        try:
            column = self.column.resolve(context)
            controller = self.controller.resolve(context)

            if column.name in controller.state.order_by and not controller.state.is_default():
                return "-%s" % (column.name)

            return column.name

        except template.VariableDoesNotExist:
            return ''


@register.tag()
def column_order(parset, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, column, controller = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            f"{token.contents.split()[0]} tag requires exactly 2 arguments")

    return ColumnOrderNone(column, controller)
