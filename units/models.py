from django.db import models
from properties.models import Property

class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.property.name})"
