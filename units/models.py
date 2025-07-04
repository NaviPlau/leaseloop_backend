from django.db import models
from properties.models import Property

class Amenity(models.Model):
    label = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.label
    
class Unit(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
        ('unavailable', 'Unavailable'),
    ]
    TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('suite', 'Suite'),
        ('cabin', 'Cabin'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    price_per_night = models.FloatField(default=0.0)
    status= models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='apartment')
    max_capacity = models.PositiveIntegerField(default=1)
    price_per_extra_person = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='units')

    def __str__(self):
        return f"{self.name} ({self.property.name})"

class UnitImage(models.Model):
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name='images'
    )
    image = models.FileField(upload_to='unit_images/', blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.unit.name}"