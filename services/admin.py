from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'price', 'property', 'created_at', 'updated_at')
    list_filter = ('type', 'property', 'created_at')
    search_fields = ('name', 'property__name')
    ordering = ('property', 'name')
