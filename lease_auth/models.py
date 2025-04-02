from django.db import models
from django.contrib.auth.models import User



class Address(models.Model):
  phone = models.CharField(max_length=20, default='0000000000')
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  street = models.CharField(max_length=100, default='Write your Streetname')
  street_number = models.CharField(max_length=10, default="0000")
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
  data_filed = models.BooleanField(default=False)
  type = models.CharField(max_length=20, default='person')
  tax_id = models.CharField(max_length=15, default='000000000')

  def __str__(self):
    return self.user


