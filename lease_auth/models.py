from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """
        Return True if the token is valid, False otherwise. A valid token is
        one that has been created within the last 15 minutes.
        """
        return now() < self.created_at + timedelta(minutes=15)
    

class LoginToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """
        Return True if the token is valid, False otherwise. A valid token is
        one that has been created within the last 7 days.
        """
        return now() < self.created_at + timedelta(days=7)

class Address(models.Model):
  phone = models.CharField(max_length=20, default='0000000000')
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  street = models.CharField(max_length=100, default='Write your Streetname')
  house_number = models.CharField(max_length=10, default="0000")
  city = models.CharField(max_length=100, default='Write your City')
  country = models.CharField(max_length=100, default='Write your Country')
  postal_code = models.CharField(max_length=10, default='00000')

  def __str__(self):
    return self.street



class Profile(models.Model):
  TYPES = (
    ('person', 'person'),
    ('company', 'company')
  )

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  address = models.ForeignKey(Address, on_delete=models.CASCADE)
  data_filled = models.BooleanField(default=False)
  type = models.CharField(max_length=20, default='person')
  tax_id = models.CharField(max_length=15, default='000000000')

  def __str__(self):
    return self.user


