from django.urls import path
from .views import generate_invoice_from_booking, OwnerInvoiceListView

urlpatterns = [
    path('generate/<int:booking_id>/', generate_invoice_from_booking, name='generate-invoice'),
    path('owner/', OwnerInvoiceListView.as_view(), name='owner-invoice-list'),
]
