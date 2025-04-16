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
            'invoice_number': generate_invoice_number(),
        }
    )

    if not created and not invoice.invoice_number:
        invoice.invoice_number = generate_invoice_number()
        invoice.save(update_fields=['invoice_number'])

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
        return Invoice.objects.all()
       # return Invoice.objects.filter(booking__client__user=user)
       # TODO: add filter for user