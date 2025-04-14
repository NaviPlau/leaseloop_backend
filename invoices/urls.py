from django.urls import path
from .views import generate_invoice_from_booking

urlpatterns = [
    path('generate/<int:booking_id>/', generate_invoice_from_booking, name='generate-invoice'),
]
