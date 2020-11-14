from math import ceil

from django.template import Node, TemplateSyntaxError, Library, Variable

register = Library()


def get_sizes(items_count, count_in_column):

    if (items_count <= count_in_column):
        return (items_count, 1)

    column_count = int(ceil(float(items_count)/count_in_column))
    rows_count = int(ceil(float(items_count)/column_count))
    return (rows_count, column_count)


def group_by(object_list, count_in_column):

    rows, columns = get_sizes(len(object_list), count_in_column)

    for i in range(rows):
        list_grouped = []
        for j in [k + i for k in range(0, len(object_list), rows)]:
            if len(object_list)>j:
                list_grouped.append(object_list[j])
            else:
                list_grouped.append(None)
        yield list_grouped


class RegroupIterNode(Node):

    def __init__(self, target, max_count_in_column, var_name):
        self.target, self.max_count_in_column = target, max_count_in_column
        self.var_name = var_name

    def render(self, context):
        obj_list = self.target.resolve(context, True)
        max_count_in_column = self.max_count_in_column.resolve(context, True)
        var_name = Variable(self.var_name).resolve(context)
        if obj_list == None:
            context[self.var_name] = []
            return ''

        context[var_name] = [i for i in group_by(obj_list, max_count_in_column)]
        return ''


def regroup_iter(parser, token):
    '''
    {% regroup_iter <list> by <max_rows_count> as <save_in_variable> %}

    '''
    bits = token.contents.split(' ')
    if len(bits) != 6:
        raise TemplateSyntaxError("tag takes six arguments")
    target = parser.compile_filter(bits[1])
    if bits[2] != 'by':
        raise TemplateSyntaxError("second argument to this tag must be 'by'")

    max_count_in_column = parser.compile_filter(bits[3])

    if bits[4] != 'as':
        raise TemplateSyntaxError("fours argument to this tag must be 'as'")

    var_name = bits[5]

    return RegroupIterNode(target, max_count_in_column, var_name)

regroup_iter = register.tag(regroup_iter)
