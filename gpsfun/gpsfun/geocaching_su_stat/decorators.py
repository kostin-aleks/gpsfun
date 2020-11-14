from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from gpsfun.main.views import updating, update
from django.contrib import messages


def it_isnt_updating(func):
    def wrapper(*args, **kwargs):
        # first argument of view allways is request
        if not updating():
            return func(*args, **kwargs)

        return update(args[0])

    return wrapper


def geocacher_su(func):
    def wrapper(*args, **kwargs):
        # first argument of view allways is request
        request = args[0]
        if request.user.is_authenticated and hasattr(request.user, 'gpsfunuser') \
           and request.user.gpsfunuser.geocacher:
            return func(*args, **kwargs)

        messages.error(
            request,
            _('Set valid nickname for geocaching.su in your profile'))
        return HttpResponseRedirect(reverse('geocaching-su'))
    return wrapper
