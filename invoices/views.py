from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from bookings.models import Booking
from .models import Invoice
from .utils import generate_invoice_pdf

@api_view(['POST'])
def generate_invoice_from_booking(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Buchung nicht gefunden'}, status=status.HTTP_404_NOT_FOUND)

    invoice, created = Invoice.objects.get_or_create(
        booking=booking,
        defaults={
            'deposit_paid': booking.deposit_paid,
            'deposit_amount': booking.deposit_amount,
            'rental_price': booking.base_renting_price,
            'rental_days': booking.total_days,
            'services_price': booking.total_services_price,
            'total_price': booking.total_price,
            'promo_code': booking.promo_code,
            'discount_amount': booking.discount_amount,
        }
    )

    if not created:
        invoice.deposit_paid = booking.deposit_paid
        invoice.deposit_amount = booking.deposit_amount
        invoice.rental_price = booking.base_renting_price
        invoice.rental_days = booking.total_days
        invoice.services_price = booking.total_services_price
        invoice.total_price = booking.total_price
        invoice.promo_code = booking.promo_code
        invoice.discount_amount = booking.discount_amount
        invoice.save()

    generate_invoice_pdf(invoice)

    return Response({
        'message': 'Rechnung erfolgreich generiert',
        'invoice_id': invoice.id,
        'pdf_file': invoice.pdf_file.url if invoice.pdf_file else None
    }, status=status.HTTP_201_CREATED)

# code below is for testing purposes only, remove in production
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def generate_invoice(request, booking_id):
    return Response({"message": f"Invoice for booking {booking_id} generated."}, status=status.HTTP_201_CREATED)
