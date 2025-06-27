from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .serializers import BookingReadSerializer, BookingWriteSerializer
from .signals import update_active_bookings
from utils.custom_pagination import CustomPageNumberPagination
from .models import Booking
from utils.custom_permission import IsOwnerOrAdmin
from .filter import apply_booking_filters

class BookingAPIView(APIView):
    permission_classes = [IsOwnerOrAdmin]
    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method.
        
        If the request method is POST, PUT, or PATCH, returns BookingWriteSerializer.
        Otherwise, returns BookingReadSerializer.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return BookingWriteSerializer
        return BookingReadSerializer

    def get(self, request, pk=None):
        """
        GET /bookings/
        Returns a list of all bookings if no pk is provided.
        If pk is provided, returns a single booking with the given pk.

        query parameters:
        - page: if provided, results will be paginated
        - any other query parameter that can be accepted by apply_booking_filters
            will be used to filter the results

        Returns 200 OK with a list of BookingReadSerializer objects if successful.
        Returns 404 NOT FOUND if a booking with the given pk is not found.
        """
        update_active_bookings()
        if pk:
            booking_obj = get_object_or_404(Booking, pk=pk)
            serializer = BookingReadSerializer(booking_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        bookings = apply_booking_filters(Booking.objects.filter(deleted=False), request)
        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(bookings, request)
            if page is not None:
                serializer = BookingReadSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        serializer = BookingReadSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST /bookings/
        Creates a new booking from the provided data.
        
        request body:
        - check_in: date of check-in
        - check_out: date of check-out
        - unit: id of the unit to book
        - guests_count: number of guests
        - services: list of ids of services to book
        - promo_code: promo code to apply (optional)
        
        Returns 201 CREATED with the created booking as a BookingReadSerializer object if successful.
        Returns 400 BAD REQUEST if the request body does not contain the required data or if the booking could not be created.
        """
        serializer = BookingWriteSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            read_serializer = BookingReadSerializer(booking)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        PATCH /bookings/{pk}/
        Updates the booking with the provided id from the provided data.
        
        request body:
        - check_in: date of check-in
        - check_out: date of check-out
        - unit: id of the unit to book
        - guests_count: number of guests
        - services: list of ids of services to book
        - promo_code: promo code to apply (optional)
        
        Returns 200 OK with the updated booking as a BookingReadSerializer object if successful.
        Returns 400 BAD REQUEST if the request body does not contain the required data or if the booking could not be updated.
        """
        booking = get_object_or_404(Booking, pk=pk)
        serializer = BookingWriteSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            booking = serializer.save()
            read_serializer = BookingReadSerializer(booking)
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        DELETE /bookings/{pk}/
        Cancels and deletes the booking with the provided id by setting its status to 'cancelled' and marking it as deleted.

        Args:
        - request: The request object.
        - pk: The primary key of the booking to be deleted.

        Returns:
        - 204 NO CONTENT: If the booking is successfully cancelled and marked as deleted.
        - 404 NOT FOUND: If no booking with the given id is found.
        """
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'cancelled'
        booking.deleted = True
        booking.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PublicBookingCreateAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        POST /public/bookings/

        Creates a new booking with the provided data.
        
        request body:
        - check_in: date of check-in
        - check_out: date of check-out
        - unit: id of the unit to book
        
        If the booking is successfully created, returns 201 CREATED with the created booking as a BookingWriteSerializer object.
        If the request body does not contain the required data, returns 400 BAD REQUEST with error messages.
        If the selected unit is no longer available, returns 409 CONFLICT with an error message.
        """
        data = request.data
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        unit_id = data.get('unit')
        if not all([check_in, check_out, unit_id]):
            return Response(
                {'error': 'Check-in, check-out and unit ID are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        overlapping = Booking.objects.filter(
            unit_id=unit_id,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in,
            deleted=False
        ).exists()
        if overlapping:
            return Response(
                {'error': 'The selected unit is no longer available.'},
                status=status.HTTP_409_CONFLICT
            )
        serializer = BookingWriteSerializer(data=data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response(BookingWriteSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)