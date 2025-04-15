from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from invoices.models import Invoice
from invoices.utils import generate_invoice_pdf

@receiver(post_save, sender=Booking)
def create_or_update_invoice(sender, instance, **kwargs):
    invoice, created = Invoice.objects.get_or_create(
        booking=instance,
        defaults={
            'deposit_paid': instance.deposit_paid,
            'deposit_amount': instance.deposit_amount,
            'rental_price': instance.base_renting_price,
            'rental_days': instance.total_days,
            'services_price': instance.total_services_price,
            'total_price': instance.total_price,
            'promo_code': instance.promo_code,
            'discount_amount': instance.discount_amount,
        }
    )
    if not created:
        invoice.deposit_paid = instance.deposit_paid
        invoice.deposit_amount = instance.deposit_amount
        invoice.rental_price = instance.base_renting_price
        invoice.rental_days = instance.total_days
        invoice.services_price = instance.total_services_price
        invoice.total_price = instance.total_price
        invoice.promo_code = instance.promo_code
        invoice.discount_amount = instance.discount_amount
        invoice.save()

    generate_invoice_pdf(invoice)

