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

# Create your views here.

class BookingAPIView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return BookingWriteSerializer
        return BookingReadSerializer

    from django.db.models import Q

    def get(self, request, pk=None):
        update_active_bookings()

        if pk:
            booking_obj = get_object_or_404(Booking, pk=pk)
            serializer = BookingReadSerializer(booking_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        bookings = Booking.objects.filter(deleted=False)

        search = request.query_params.get('search')
        if search:
            bookings = bookings.filter(
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search) |
                Q(property__name__icontains=search) |
                Q(unit__name__icontains=search) | 
                Q(property__address__city__icontains=search) |
                Q(property__address__country__icontains=search) |
                Q(property__address__street__icontains=search) 
            )

        if not request.user.is_staff:
            bookings = bookings.filter(unit__property__owner=request.user)

        bookings = bookings.order_by('check_in')

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
