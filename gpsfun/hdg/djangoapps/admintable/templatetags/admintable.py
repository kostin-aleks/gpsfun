from django import template
register = template.Library()
from django.utils.html import conditional_escape

@register.inclusion_tag('AdminTable/render_search_field.html')
def render_search_field(field):
    ftype = 'text'
    if field.db_type()[:7]=='integer':
        ftype='integer'
    if field.db_type()=='datetime':
        ftype='datetime'
    else:
        print(field.db_type())

    return dict(field=field,
                ftype=ftype)

@register.simple_tag
def cell_format(s):
    if hasattr(s,'_meta'):
        meta = s._meta
        res = '<a href="/YP-admin/admin/%s/%s/%d/">%s</a>' % (\
            meta.app_label,
            meta.module_name,
            s.id,
            s)
    else:
        res = conditional_escape(s)
    return res
