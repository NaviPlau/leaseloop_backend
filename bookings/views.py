from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .serializers import BookingReadSerializer, BookingWriteSerializer
from .signals import update_active_bookings
from utils.custom_pagination import CustomPageNumberPagination
from .models import Booking
from django.db.models import Q
from utils.custom_permission import IsOwnerOrAdmin
from .filter import apply_booking_filters
from rest_framework.generics import CreateAPIView

class BookingAPIView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return BookingWriteSerializer
        return BookingReadSerializer

    def get(self, request, pk=None):
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
        serializer = BookingWriteSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            read_serializer = BookingReadSerializer(booking)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        serializer = BookingWriteSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            booking = serializer.save()
            read_serializer = BookingReadSerializer(booking)
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'cancelled'
        booking.deleted = True
        booking.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PublicBookingCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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