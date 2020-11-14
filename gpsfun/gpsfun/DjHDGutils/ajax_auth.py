#!/usr/bin/env python

# auth decorators intended to use with accept_ajax

from django.utils.translation import ugettext_lazy as _

def login_required_ajax(view):
    """ check that user logged in

        use as decorator below @accept_ajax """

    def f(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return dict(result='error',
                        message=unicode(_('Your connection has expired. Please log in again')))

        return view(request, *args, **kwargs)

    return f

def permission_required_ajax(permission):
    """ check that user has permission

        use as decorator below accept_ajax """

    def decorator(view):
        def f(request, *args, **kwargs):

            permission = 'translation.modify_translations'
            if not request.user.has_perm(permission):
                return dict(result='error',
                            message=unicode(_('You have not {0} permission'.format(permission)))
                            )

            return view(request, *args, **kwargs)

        return f
    return decorator


