from django.db import models

class Service(models.Model):
    STATUS_CHOICES = [
        ('one_time', 'One Time'),
        ('per_day', 'Per Day'),
    ]
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0.0)
    type = models.CharField(max_length=20, choices=STATUS_CHOICES, default='one_time')
    property = models.ForeignKey(
        'properties.Property', on_delete=models.CASCADE, related_name='services'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.type})"