from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from hdg.djangoapps.admin_index.models import Bookmark
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from hdg.djangoapps.admin_index import custom_admin_index

#from tf.custom.admin2.dashboard_settings import columns, LOGO

@staff_member_required
def index(request):
    return direct_to_template(request, 'manage/new_index.html',
        {'current_site': Site.objects.get(id=settings.SITE_ID),
         'users_count': User.objects.all().count(),
         'page': custom_admin_index,
         'logo': '/manage/images/logo.png',
         }
                              )


@staff_member_required
def add_extbookmark(request):
    ExternalBookmark(user=request.user,
                     title=request.POST.get('title'),
                     link=request.POST.get('url'),
                     is_public = request.POST.get('public') == 'on').save()
    return HttpResponse('OK')

@staff_member_required
def del_extbookmark(request):
    ExternalBookmark.objects.get(id=request.POST.get('link_id')).delete()
    return HttpResponseRedirect(reverse('manage-index'))
