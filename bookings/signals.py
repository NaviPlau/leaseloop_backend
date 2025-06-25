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
    """
    Signal receiver for Booking post_save signal.

    If the booking status is "confirmed", creates a new invoice with a unique invoice number, 
    or updates the existing invoice if it does not have an invoice number.  
    
    If the booking property owner's email is not "guest@exampless.com", sends an email to the client
    with the invoice as an attachment, if the invoice has a pdf file attached.

    :param sender: The sender of the post_save signal (Booking model)
    :param instance: The booking instance that triggered the signal
    :param kwargs: Additional keyword arguments from the signal
    """
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
        """
        Sets active=False for all bookings whose check_out date is today or in the future.

        This function is meant to be called as a cron job, once a day, to update the active
        status of bookings accordingly. It is also called when a booking is confirmed, so
        that the newly confirmed booking is marked as active.
        """
        today = timezone.now().date()
        Booking.objects.filter(check_out__gte=today).update(active=False)