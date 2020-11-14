from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from hdg.djangoapps.simplecms.models import TextBlock, Link, LinksList, Navigation, FlatPageImage, FlatPageFile, SiteSettings, CSSDesignSkin
from django.contrib.flatpages.models import FlatPage


class TextBlockAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display=('slug','order','is_displayed')


class LinkInline(admin.TabularInline):
    model = Link

class LinksListAdmin(admin.ModelAdmin):
    inlines = [
        LinkInline,
    ]
    prepopulated_fields = {"slug": ("title",)}
    list_display=('slug','order','is_displayed')
    
class ObjectTreeAdmin(admin.ModelAdmin):
    list_display=('short_title', 'content_object_info', 'uplink', 'added', 'changed', 'is_displayed', 'sort_order')


class FlatPageImageInline(admin.StackedInline):
    model = FlatPageImage

class FlatPageFileInline(admin.StackedInline):
    model = FlatPageFile


class FlatPageAdmin(admin.ModelAdmin):
    class Media:
        js = ('tiny_mce/js/tiny_mce.js',
              'MochiKit/js/MochiKit.js',
              'tiny_mce/js/textarea.js',
              )
              
    inlines = [
        FlatPageImageInline,
        FlatPageFileInline,
        ]

class SiteSettingsAdmin(admin.ModelAdmin):
    pass


class CSSDesignSkinAdmin(admin.ModelAdmin):
    list_display = ['title', 'css_file', 'pageid_regexp', 'sort_order']

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(TextBlock, TextBlockAdmin)
admin.site.register(LinksList, LinksListAdmin)
admin.site.register(Navigation, ObjectTreeAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(CSSDesignSkin, CSSDesignSkinAdmin)
