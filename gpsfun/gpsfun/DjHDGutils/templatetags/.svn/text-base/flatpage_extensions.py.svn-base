from django.contrib.flatpages.models import FlatPage
from django import template
import re

register = template.Library()

@register.simple_tag
def display_flatpage_content(page_url):
    return FlatPage.objects.get(url=page_url).content

class FlatePageIndexObject(template.Node):
    def __init__(self,store_to_variable_name, flatpages_re):
        self.store_to_variable_name = store_to_variable_name
        self.flatpages_re = flatpages_re

    def render(self, context):
        flatpages_re = template.Variable(self.flatpages_re).resolve(context)
        var_name = template.Variable(self.store_to_variable_name).resolve(context)
        matched_flatpages = []
        index_pattern = re.compile(flatpages_re)
        for fp in FlatPage.objects.all().order_by('title'):
            if re.match(index_pattern,fp.url):
                matched_flatpages.append(fp)
        context[var_name]=matched_flatpages
        return ''

def get_flatpage_index(parser, token):
    """
    {% get_flatpage_index <store_to_variable_name> <flatpages_regular_expression> %}

    Example:
    {% get_flatpage_index 'information' '^/info/' %} will store all
    flatpages with URL starting from '/info/' to variable naled 'information' 

    """
    arr = token.split_contents()
    store_to_variable_name, flatpages_re = (arr[1],arr[2])
    return FlatePageIndexObject(store_to_variable_name, flatpages_re)


register.tag('get_flatpage_index', get_flatpage_index)
