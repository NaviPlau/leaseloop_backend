from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from addresses.models import Address
from .models import Profile, UserLogo

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a new profile instance after a new user is created.

    Listens to the post_save signal sent by the User model. If the user is created
    (i.e. created=True), it creates a new profile instance associated with the user.
    The profile instance is populated with some default values like a default address
    and a default logo.

    :param sender: The model that sent the post_save signal.
    :param instance: The instance of the model that was saved.
    :param created: A boolean indicating whether the instance was created or updated.
    :param kwargs: Additional keyword arguments passed to the signal.
    """
    if created:
        address = Address.objects.create(
            street='Example Street',
            house_number='222',
            postal_code='00000',
            city='Example City',
            country='Narnia',
            phone='000000000'
        )
        logo = UserLogo.objects.create(user=instance, logo=None)
        Profile.objects.create(
            user=instance,
            data_filled=False,
            tax_id='000000000',
            address=address,
            logo=logo
        )