from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from bookings.models import Booking
from .models import Invoice
from .utils import generate_invoice_pdf
from rest_framework.views import APIView
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated
from utils.custom_pagination import CustomPageNumberPagination
from django.db.models import Q
from .utils import generate_invoice_number
from utils.custom_permission import IsOwnerOrAdmin


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
        'pdf_file': invoice.pdf_file.url if invoice.pdf_file else None,
        'logo_path': invoice.logo.logo.url if hasattr(invoice, 'logo') and invoice.logo and invoice.logo.logo else None
    }, status=status.HTTP_201_CREATED)



class OwnerInvoiceListView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request):
        """
        Returns a list of invoices where the logged-in user is the owner
        of the related booking's property. Supports ?search= and ?page=
        """
        user = request.user

        # 🟢 Base queryset
        invoices = Invoice.objects.filter(booking__property__owner=user)

        # 🔍 Optional search filter
        search = request.query_params.get('search')
        if search:
            invoices = invoices.filter(
                Q(booking__client__first_name__icontains=search) |
                Q(booking__client__last_name__icontains=search) |
                Q(booking__property__name__icontains=search) |
                Q(booking__unit__name__icontains=search) |
                Q(invoice_number__icontains=search) |
                Q(booking__property__address__city__icontains=search) |
                Q(booking__property__address__country__icontains=search) |
                Q(booking__property__address__street__icontains=search)
            )

        # ✅ Pagination if ?page= is provided
        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(invoices, request)
            if page is not None:
                serializer = InvoiceSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        # ❌ No pagination → return all
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)