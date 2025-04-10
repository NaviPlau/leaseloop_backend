from django.db import models
from addresses.models import Address

# Create your models here.
class Client(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    address = models.OneToOneField(
        'addresses.Address',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='client'
    )
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='clients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"