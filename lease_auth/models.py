from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from addresses.models import Address


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
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)

  def __str__(self):
    return self.address
  

class UserLogo(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  logo = models.FileField(upload_to='logos/')

  def __str__(self):
    return self.user



class Profile(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  data_filled = models.BooleanField(default=False)
  tax_id = models.CharField(max_length=15, default='000000000')

  def __str__(self):
    return self.user


