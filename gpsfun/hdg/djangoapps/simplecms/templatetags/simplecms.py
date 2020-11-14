from django.template import Library, Node, Variable
from django.template.loader import render_to_string

from hdg.djangoapps.simplecms.models import LinksList, TextBlock, Navigation


register = Library()

@register.inclusion_tag('link_list.html')
def link_list(list_name):
    list_name=u''+list_name
    try:
        link_list = LinksList.objects.get(slug=list_name)
    except LinksList.DoesNotExist:
        return {}
    return dict(link_list=link_list)

@register.inclusion_tag('simple_menu.html')
def simple_menu(list_name, selected):
    list_name=u''+list_name
    try:
        link_list = LinksList.objects.get(slug=list_name)
    except LinksList.DoesNotExist:
        return {}
    return dict(selected=selected,
                link_list=link_list)


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



class BranchesObject(Node):
    def __init__(self,store_to_variable_name, uplink):
        self.store_to_variable_name = store_to_variable_name
        self.uplink = uplink

    def render(self, context):
        var_name = Variable(self.store_to_variable_name).resolve(context)
        if self.uplink:
            uplink = Variable(self.uplink).resolve(context)
        else:
            uplink = self.uplink
        try:
            objects_list = Navigation.objects.filter(uplink=uplink).order_by('sort_order')
        except TextBlock.DoesNotExist:
            return ''
        context[var_name]=objects_list
        return ''

def get_branches(parser, token):
    """
    {% get_branches <store_to_variable_name> <uplink> %}
    """
    arr = token.split_contents()
    store_to_variable_name = arr[1]
    if len(arr) == 2:
        uplink = None
    else:
        uplink = arr[2]
    return BranchesObject(store_to_variable_name, uplink)


register.tag('get_branches', get_branches)


def sort_branches(branches, uplink_id, level=0, open_all_branches=False):
    out  = []
    for branch in branches.values():
        if (branch.uplink is None and uplink_id is None) or \
               (uplink_id and branch.uplink and \
                branch.uplink.id == uplink_id):
            branch.level = level
            out.append(branch)

    def my_cmp(a,b):
        return cmp(a.sort_order,b.sort_order)

    out.sort(my_cmp)

    # add sub-level items after each one
    out2 = []
    for item in out:
        out2.append(item)
        if item.selected or open_all_branches:
            out2 += sort_branches(branches, item.id, level+1)

    if out2:
        prev_level = out2[0].level
    for i in out2:
        i.add_level = 0
        i.close_level = 0
        if i.level > prev_level:
            i.add_level = ['<ul>'] * (i.level - prev_level)
        elif i.level < prev_level:
            i.close_level = ['</ul>'] * (prev_level - i.level)
        prev_level = i.level
    return out2
    

def calc_deeplevel(arr):
    level = 0
    for item in arr:
        if item.add_level:
            level += 1
        elif item.close_level:
            level -= 1
    return level


def mark_selected_uptree(tree, selected_item_id):
    tree[selected_item_id].selected = True
    if tree[selected_item_id].uplink:
        mark_selected_uptree(tree, tree[selected_item_id].uplink.id)
    


@register.inclusion_tag('navigation_tree.html', takes_context=True)
def navigation_tree(context):
    branches = {}
    selected_branch_id = None
    for branch in Navigation.objects.all():
        if branch.content_object and \
               branch.content_object.get_absolute_url()==context['PATH_INFO']:
            branch.selected = True
            selected_branch_id = branch.id
        else:
            branch.selected = False
        branches[branch.id]=branch

    if selected_branch_id:
        mark_selected_uptree(branches, selected_branch_id)

    sorted_branches = sort_branches(branches, None)
    
    context['tree'] = sorted_branches
    context['deeplevel'] = ['']*calc_deeplevel(sorted_branches)
    
    return context

class ContentManagementBlockObject(Node):

    def render(self, context):
        if context['is_staff']:
            
            return render_to_string('content_management_box.html', context)
        
        else:
            return ''

def content_management_box(parser, token):
    return ContentManagementBlockObject()


register.tag('content_management_box', content_management_box)

