# from django.contrib import admin
# from django.utils.translation import ugettext_lazy as _
# from django.contrib.flatpages.models import FlatPage
# from hdg.djangoapps.news.models import NewsArticle, NewsArticlePhoto
# 
# 
# class NewsArticlePhotoInline(admin.TabularInline):
#     model = NewsArticlePhoto
# 
# 
# class NewsArticleAdmin(admin.ModelAdmin):
#     prepopulated_fields = {
#         "slug": ('title','language')
#         }
#     list_display = ('slug','pub_date','title','language')
#     list_filter = ('pub_date','language')
# 
#     class Media:
#         js = ('tiny_mce/js/tiny_mce.js',
#               'MochiKit/js/MochiKit.js',
#               'tiny_mce/js/textarea.js',
#               )
# 
#     inlines = [
#         NewsArticlePhotoInline
#         ]
# 
# admin.site.register(NewsArticle, NewsArticleAdmin)

