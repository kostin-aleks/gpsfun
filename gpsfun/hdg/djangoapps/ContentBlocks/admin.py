from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from hdg.djangoapps.ContentBlocks.models import TextBlock, Link, LinkList, TreeBranch, FlatPageImage
from django.contrib.flatpages.models import FlatPage
from django.contrib import databrowse


class TextBlockAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display=('slug','order','is_displayed')


class LinkInline(admin.TabularInline):
    model = Link

class LinkListAdmin(admin.ModelAdmin):
    inlines = [
        LinkInline,
    ]
    prepopulated_fields = {"slug": ("title",)}
    list_display=('slug','order','is_displayed')
    
class TreeBranchAdmin(admin.ModelAdmin):
    list_display=('object_id', 'uplink', 'added', 'changed', 'is_displayed', 'sort_order')


class FlatPageImageInline(admin.StackedInline):
    model = FlatPageImage


class FlatPageAdmin(admin.ModelAdmin):
    class Media:
        js = ('tiny_mce/js/tiny_mce.js',
              'tiny_mce/js/textarea.js',)
    inlines = [
        FlatPageImageInline,
        ]
    

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)


admin.site.register(TextBlock, TextBlockAdmin)
admin.site.register(LinkList, LinkListAdmin)
admin.site.register(TreeBranch, TreeBranchAdmin)
