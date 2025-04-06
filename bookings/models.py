from django.db import models

# Create your models here.
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    unit_id = models.CharField(max_length=200)
    client_id = models.ForeignKey("apps.clients.Model", on_delete=models.CASCADE) #one-to-one
    check_in = models.DateField()	
    check_out = models.DateField()
    guests = models.IntegerField()
    total_price = models.FloatField()
    deposit_paid = models.BooleanField(default=False)
    deposit_amount = models.FloatField(default=0.0)
    status = models.ChoicesField(choices=STATUS_CHOICES, default='pending')
    services = models.ManyToOneRelatedField("apps.services.Model", on_delete=models.CASCADE) #many-to-many
    #promo_code = models.ForeignKey("apps.promos.Model", on_delete=models.CASCADE) #one-to-one
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)