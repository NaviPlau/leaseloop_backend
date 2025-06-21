from django.contrib import admin
# from .models import Booking

# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'client', 'unit', 'check_in', 'check_out',
#         'guests_count', 'status', 'total_price', 'deposit_paid',
#         'created_at', 'updated_at'
#     )
#     list_filter = ('status', 'deposit_paid', 'created_at', 'updated_at')
#     search_fields = ('client__first_name', 'client__last_name', 'unit__name')
#     ordering = ('-created_at',)
#     date_hierarchy = 'check_in'
#     filter_horizontal = ('services',)
