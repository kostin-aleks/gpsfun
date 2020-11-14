from django.contrib import admin
from hdg.djangoapps.AttributeEngine.models import AttributeGroup, AttributeGroupField

class AttributeGroupAdmin(admin.ModelAdmin):
    pass

class AttributeGroupFieldAdmin(admin.ModelAdmin):
    pass


admin.site.register(AttributeGroup, AttributeGroupAdmin)
admin.site.register(AttributeGroupField, AttributeGroupFieldAdmin)

