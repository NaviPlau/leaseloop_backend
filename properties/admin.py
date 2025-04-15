from django.contrib import admin
from .models import Property, PropertyImage

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'address', 'created_at', 'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', )

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'alt_text', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('property__name', 'alt_text')
