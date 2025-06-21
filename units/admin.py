from django.contrib import admin
# from .models import Unit, UnitImage

# @admin.register(Unit)
# class UnitAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'name',
#         'property',
#         'type',
#         'capacity',
#         'max_capacity',
#         'price_per_night',
#         'price_per_extra_person',
#         'status',
#     )
#     list_filter = ('property', 'type', 'status')
#     search_fields = ('name', 'property__name')
#     ordering = ('property', 'name')

# @admin.register(UnitImage)
# class UnitImageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'unit', 'alt_text', 'created_at', 'updated_at')
#     search_fields = ('unit__name', 'alt_text')
#     list_filter = ('created_at', 'updated_at')
