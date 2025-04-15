from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'booking', 'total_price', 'deposit_paid',
        'promo_code', 'payment_status', 'created_at', 'updated_at'
    )
    list_filter = ('deposit_paid', 'promo_code', 'payment_status', 'created_at', 'updated_at')
    search_fields = ('booking__id', 'booking__client__email')
