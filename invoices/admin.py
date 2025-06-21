# from django.contrib import admin
# from .models import Invoice

# @admin.register(Invoice)
# class InvoiceAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'invoice_number',
#         'booking',
#         'payment_status',
#         'created_at',
#         'updated_at',
#         'pdf_download_link',
#     )
#     list_filter = ('payment_status', 'created_at', 'updated_at')
#     search_fields = ('invoice_number', 'booking__id', 'booking__client__email')

#     def pdf_download_link(self, obj):
#         if obj.pdf_file:
#             return f"<a href='{obj.pdf_file.url}' target='_blank'>Download PDF</a>"
#         return "No PDF"
#     pdf_download_link.allow_tags = True
#     pdf_download_link.short_description = "PDF"
