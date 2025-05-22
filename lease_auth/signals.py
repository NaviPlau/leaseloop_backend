from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from addresses.models import Address
from .models import Profile, UserLogo

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
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