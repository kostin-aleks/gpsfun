from django.template import Library, Node, Variable
from hdg.djangoapps.ContentBlocks.models import LinkList, TextBlock
from django.utils.encoding import force_unicode

register = Library()

@register.inclusion_tag('link_list.html')
def link_list(list_name):
    list_name=u''+list_name
    try:
        link_list = LinkList.objects.get(slug=list_name)
    except LinkList.DoesNotExist:
        return {}
    return dict(link_list=link_list)

@register.simple_tag
def text_block(block_name):
    block_name=u''+block_name
    try:
        text = TextBlock.objects.get(slug=block_name)
    except TextBlock.DoesNotExist:
        return ''
    return text.text

@register.simple_tag
def text_block_title(block_name):
    block_name=u''+block_name
    try:
        text = TextBlock.objects.get(slug=block_name)
    except TextBlock.DoesNotExist:
        return ''
    return text.title


class TextBlockObject(Node):
    def __init__(self,store_to_variable_name, block_name):
        self.store_to_variable_name = store_to_variable_name
        self.block_name = block_name

    def render(self, context):
        block_name = Variable(self.block_name).resolve(context)
        var_name = Variable(self.store_to_variable_name).resolve(context)
        try:
            text = TextBlock.objects.get(slug=block_name)
        except TextBlock.DoesNotExist:
            return ''
        context[var_name]=text
        return ''

def get_text_block(parser, token):
    """
    {% get_text_block <store_to_variable_name> <block_slug> %}
    """
    arr = token.split_contents()
    store_to_variable_name, block_slug = (arr[1],arr[2])
    return TextBlockObject(store_to_variable_name, block_slug)


register.tag('get_text_block', get_text_block)
