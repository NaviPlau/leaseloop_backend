from django.core.management.base import BaseCommand
from django.utils.timezone import now
from promocodes.models import Promocodes

class Command(BaseCommand):
    help = 'Deactivate expired promo codes based on valid_until date'

    def handle(self, *args, **kwargs):
        expired = Promocodes.objects.filter(valid_until__lt=now().date(), active=True)
        count = expired.update(active=False)
        self.stdout.write(f'{count} expired promo codes deactivated.')