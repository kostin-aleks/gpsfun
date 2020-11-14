from django.contrib import admin
from hdg.djangoapps.RuntimeSettings.models import RuntimeVariable, RuntimeCategory

class RuntimeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(RuntimeCategory, RuntimeCategoryAdmin)


class RuntimeVariableAdmin(admin.ModelAdmin):
    list_display = ('key', 'localized_description', 'category', 'value', 'modified')
    search_fields = ('key', 'description')
    list_filter = ('category', )


admin.site.register(RuntimeVariable, RuntimeVariableAdmin)
