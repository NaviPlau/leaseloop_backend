from django.db import models
from django.conf import settings
from addresses.models import Address
class Property(models.Model):
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties'
    )
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, default='narnia@dream.com')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='properties')
    description = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, related_name='images'
    )
    image = models.FileField(upload_to='property_images/', blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.property.name}"
