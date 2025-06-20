from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from invoices.models import Invoice
from invoices.utils import generate_invoice_number, generate_invoice_pdf
from bookings.models import Booking
from django.utils import timezone


@receiver(post_save, sender=Booking)
def create_or_update_invoice(sender, instance, **kwargs):
    if instance.status != "confirmed":
        return
    
    invoice, created = Invoice.objects.get_or_create(
        booking=instance,
        defaults={
            'invoice_number': generate_invoice_number(),
            
        }
    )
    if not created and not invoice.invoice_number:
        invoice.invoice_number = generate_invoice_number()
        invoice.save(update_fields=['invoice_number'])

    generate_invoice_pdf(invoice)

    if instance.property.owner.email == "guest@exampless.com":
        return

    email = EmailMessage(
        subject="Your Booking Confirmation – LeaseLoop",
        body=render_to_string("emails/booking_confirmation.html", {"booking": instance}),
        from_email="noreply@lease-loop.com",
        to=[instance.client.email],
    )
    email.content_subtype = "html"

    if invoice.pdf_file:
        email.attach_file(invoice.pdf_file.path)

    email.send()


def update_active_bookings():
        today = timezone.now().date()
        Booking.objects.filter(check_out__gte=today).update(active=False)