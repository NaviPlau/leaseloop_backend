from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property
from units.models import Amenity
from units.amenities_data import amenity_list


@receiver(post_save, sender=Property)
def create_default_amenities(sender, instance, created, **kwargs):
    if created and Amenity.objects.count() == 0:
      for item in amenity_list:
        Amenity.objects.create(label=item["label"], category=item["category"])