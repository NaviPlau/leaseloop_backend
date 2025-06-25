from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property
from units.models import Amenity
from units.amenities_data import amenity_list

@receiver(post_save, sender=Property)
def create_default_amenities(sender, instance, created, **kwargs):
    """
    Signal receiver that creates default amenities for a Property instance.

    This function listens for the `post_save` signal from the `Property` model. 
    If a new Property instance is created and there are no existing amenities, 
    it populates the database with a predefined list of amenities.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Property): The instance of the Property model that was saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.
    """

    if created and Amenity.objects.count() == 0:
      for item in amenity_list:
        Amenity.objects.create(label=item["label"], category=item["category"])