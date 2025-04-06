from django.db import models
from clients.models import Client
from services.models import Service
from promocodes.models import Promocodes
from units.models import Unit 


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE) 
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    total_price = models.FloatField()

    deposit_paid = models.BooleanField(default=False)
    deposit_amount = models.FloatField(default=0.0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    services = models.ManyToManyField(Service, blank=True)
    promo_code = models.ForeignKey(Promocodes, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} for {self.client}"
