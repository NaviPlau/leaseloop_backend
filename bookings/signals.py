from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from invoices.models import Invoice
from invoices.utils import generate_invoice_number, generate_invoice_pdf

from django.template.loader import render_to_string
from django.conf import settings
import os
from xhtml2pdf import pisa



from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from invoices.models import Invoice
from invoices.utils import generate_invoice_number, generate_invoice_pdf

@receiver(post_save, sender=Booking)
def create_or_update_invoice(sender, instance, **kwargs):
    invoice, created = Invoice.objects.get_or_create(
        booking=instance,
        defaults={
            'invoice_number': generate_invoice_number(),
        }
    )

    if not created:
        if not invoice.invoice_number:
            invoice.invoice_number = generate_invoice_number()
            invoice.save(update_fields=['invoice_number'])

    generate_invoice_pdf(invoice)


    #TODO: send email with invoice to user