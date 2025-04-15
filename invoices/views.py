from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from bookings.models import Booking
from .models import Invoice
from .utils import generate_invoice_pdf
from rest_framework.generics import ListAPIView
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def generate_invoice_from_booking(request, booking_id):
    """
    Generate an invoice for a booking.

    Given a booking id, this API call will generate an invoice
    for the booking. The invoice will be saved to the database and
    a PDF will be generated.

    Parameters:
        booking_id: The id of the booking to generate the invoice for

    Returns:
        A JSON response containing the invoice id, a message and the
        URL of the PDF file if it was successfully generated.
    """
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

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
        'message': 'Invoice generated successfully',
        'invoice_id': invoice.id,
        'pdf_file': invoice.pdf_file.url if invoice.pdf_file else None
    }, status=status.HTTP_201_CREATED)


class OwnerInvoiceListView(ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of invoices for the current user.

        :return: A list of Invoice objects
        """
        user = self.request.user
        return Invoice.objects.filter(booking__client__user=user)
