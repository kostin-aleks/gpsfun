from django import template
from django.template import Variable
from django.conf import settings
import types

from gpsfun.tableview.models import TableViewProfile

register = template.Library()


class TicketProfilesNode(template.Node):
    def __init__(self, user, tableview_name, save_to):
        self.user = Variable(user)
        self.tableview_name = Variable(tableview_name)
        self.save_to = Variable(save_to)


    def render(self, context):
        context[self.save_to.resolve(context)] = \
            TableViewProfile.objects.filter(
                user=self.user.resolve(context),
                tableview_name=self.tableview_name.resolve(context),
                is_default=False).order_by('label')
        return ''


@register.tag()
def tableview_profiles(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, user, tableview_name, save_to = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly 3 arguments" % token.contents.split()[0])

    return TicketProfilesNode(user, tableview_name, save_to)
