from django.db import models
from properties.models import Property

class Unit(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    status= models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    max_capacity = models.PositiveIntegerField(default=1)
    price_per_extra_person = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)


    def __str__(self):
        return f"{self.name} ({self.property.name})"

class UnitImage(models.Model):
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name='images'
    )
    image = models.FileField(upload_to='unit_images/', blank=True) #define the upload path
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.property.name}"