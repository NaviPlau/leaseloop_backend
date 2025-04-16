from django.db import models
from bookings.models import Booking
from promocodes.models import Promocodes

class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
    ('unpaid', 'Unpaid'),
    ('paid', 'Paid'),
    ('partially_paid', 'Partially Paid'),
]

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.id} for Booking #{self.booking.id}"
