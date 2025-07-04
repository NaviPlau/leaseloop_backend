from django.db import models
from clients.models import Client
from services.models import Service
from promocodes.models import Promocodes
from units.models import Unit 
from properties.models import Property

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guests_count = models.PositiveIntegerField()
    total_price = models.FloatField(default=0.0)
    total_days = models.PositiveIntegerField(default=1)
    deposit_paid = models.BooleanField(default=False)
    deposit_amount = models.FloatField(default=0.0, )
    base_renting_price = models.FloatField(default=0.0, )
    total_services_price = models.FloatField(default=0.0,)
    active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, related_name='bookings', null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL,related_name='bookings', null=True, blank=True)
    services = models.ManyToManyField(Service, related_name='bookings', blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='bookings', null=True, blank=True)
    promo_code = models.ForeignKey(Promocodes, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


