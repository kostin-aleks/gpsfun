from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from hdg.djangoapps.simplecms.models import Navigation
from django.contrib.flatpages.models import FlatPage
from django.template.defaultfilters import slugify
from django.contrib.sites.models import Site

def unique_str():
    return "%s"  % slugify(datetime.now().ctime())

def nav_addobj(request, path):
    path = '/'+path
    title = 'New object. %s' % unique_str()
    if request.method == 'POST':
        ctype = ContentType.objects.get(name=request.POST['obj_type'])
        newobj = ctype.model_class()()
        for field in newobj._meta.fields:
            if not field.blank:
                if field.get_internal_type()=='CharField':
                    setattr(newobj, field.name, unique_str())
                else:
                    print 'Error: no default can be set for field %s of type %s' % (field, field.get_internal_type())
        newobj.save()

        if request.POST['obj_type']=='flat page':
            newobj.sites.add(Site.objects.get_current())
            newobj.url = path+unique_str()+'/'
            for par in ['title','url']:
                if par in request.POST:
                    setattr(newobj, par, request.POST[par])
            title = newobj.title
            newobj.save()
        

    uplink = None

    if path!='/':
        uplink_flatpage = None
        try:
            uplink_flatpage = FlatPage.objects.get(url = path)
        except FlatPage.DoesNotExist:
            pass
        if uplink_flatpage:
            uplinks = Navigation.objects.filter(object_id = uplink_flatpage.id,
                                                content_type = ContentType.objects.get_for_model(FlatPage))
            if len(uplinks)>=1:
                uplink=uplinks[0]
            
    navigation_element = Navigation(short_title = title,
                                    content_type = ctype,
                                    object_id = newobj.id,
                                    uplink = uplink)
    navigation_element.save()
    
    return HttpResponseRedirect(path)

def find_flatpage_nav(path):
    flatpage = FlatPage.objects.get(url = path)
    nav = Navigation.objects.filter(object_id = flatpage.id,
                                    content_type = ContentType.objects.get_for_model(FlatPage))
    if len(nav)>=1:
        return nav[0]
    if len(nav)==0:
        return None

def nav_delobj(request, path):
    path = '/'+path
    flatpage = FlatPage.objects.get(url = path)
    if path!='/':
        nav = find_flatpage_nav(path)
        if nav:
            nav.delete()
        flatpage.delete()
        
    return HttpResponseRedirect('/')

def editobj(request,path):
    path = '/'+path
    flatpage = FlatPage.objects.get(url = path)
    return HttpResponseRedirect('/admin/flatpages/flatpage/%d/' % flatpage.id)


def editnav(request,path):
    path = '/'+path
    nav = find_flatpage_nav(path)
    if nav:
        return HttpResponseRedirect('/admin/simplecms/navigation/%d/' % nav.id)
    else:
        # TODO: show page asking where to ass this item to nav
        return HttpResponseRedirect('/admin/simplecms/navigation/add/')
        
    
