from django.db import models
from bookings.models import Booking
import os

class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
    ('unpaid', 'Unpaid'),
    ('paid', 'Paid'),
    ('partially_paid', 'Partially Paid'),
]

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, related_name='invoice')
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.id} for Booking #{self.booking}"
    
    def delete(self, *args, **kwargs):
        """
        Deletes the Invoice instance and removes the associated PDF file
        from the file system if it exists.
        """
        if self.pdf_file and os.path.isfile(self.pdf_file.path):
            os.remove(self.pdf_file.path)
        super().delete(*args, **kwargs)
