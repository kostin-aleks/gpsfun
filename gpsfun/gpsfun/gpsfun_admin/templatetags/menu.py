"""
menu
"""

from django import template

register = template.Library()


@register.inclusion_tag('menu.html')
def show_menu():
    """ show menu """
    menu = []

    menu.append({'title': 'GPS-FUN admin',
              'submenu': [{'title': 'Home', 'url': '/gpsfun-admin/'},
                          ]})

    menu.append({'title': 'System',
              'submenu': [
                  {'title': 'Data updating log', 'url': '/gpsfun-admin/data_updating_log/'},
                  {'title': 'Last updating', 'url': '/gpsfun-admin/last_updates/'},
              ]})

    menu.append({'title': 'Logout', 'url': '/gpsfun-admin/logout/'})

    return dict(menu=menu)
