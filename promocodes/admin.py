# from django.contrib import admin
# from .models import Promocodes

# @admin.register(Promocodes)
# class PromocodeAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'code', 'description', 'discount_percent',
#         'valid_until', 'owner_id', 'created_at', 'updated_at'
#     )
#     list_filter = ('valid_until', 'created_at', 'updated_at')
#     search_fields = ('code', 'description', 'owner_id__email')
#     ordering = ('-created_at',)
