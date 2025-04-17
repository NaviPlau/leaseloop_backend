from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Promocodes(models.Model):
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    valid_until = models.DateField()
    discount_percent = models.FloatField(verbose_name=("discount percent"), default=0.0)
    owner_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,related_name='promocodes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)