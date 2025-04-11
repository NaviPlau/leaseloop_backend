from django.db import models
from django.conf import settings
from addresses.models import Address
class Property(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties'
    )
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='properties')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='images'
    )
    image = models.FileField(upload_to='property_images/', blank=True) #define the upload path
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.property.name}"
