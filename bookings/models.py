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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,related_name='bookings', null=True, blank=True)
    services = models.ManyToManyField(Service, related_name='bookings', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    promo_code = models.ForeignKey(Promocodes, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # def save(self, *args, **kwargs):
    # # Tage berechnen
    #     self.total_days = (self.check_out - self.check_in).days
    #     if self.total_days <= 0:
    #         self.total_days = 1


    #     # Rabatt
    #     if self.promo_code:
    #         self.discount_amount = (self.base_renting_price * (self.promo_code.discount_percent / 100))

    #     self.total_price = self.base_renting_price + self.total_services_price - self.discount_amount

    #     super().save(*args, **kwargs)
    



    # percent of the promo code
    # dicsount amount
    # total price
    # total days
    # created at
    # deposit amount
    # total services pricing



    # base_renting_price = (unit price per night + (unit_extra_person_price * (guests_count - unit_max-capacity))) * total_days
    # total_services_price = sum(service.price for service in services)  if services.service.type = per_day  serviceprice*guests_count else service.price
    # total_renting_price = (base_renting_price + total_services_price ) -  discount_amount
    # discountamount = (base_renting_price * (promo_code.percent/100))

