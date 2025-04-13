from django.db import models
from bookings.models import Booking
from promocodes.models import Promocodes

class Invoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    deposit_paid = models.BooleanField(default=False)
    deposit_amount = models.FloatField(default=0.0)
    rental_price = models.FloatField(default=0.0) 
    rental_days = models.PositiveIntegerField(default=1)
    services_price = models.FloatField(default=0.0) 
    total_price = models.FloatField(default=0.0)
    promo_code = models.ForeignKey(Promocodes, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.FloatField(default=0.0)

    generated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rechnung #{self.id} für Buchung #{self.booking.id}"
