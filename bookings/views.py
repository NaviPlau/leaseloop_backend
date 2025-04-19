from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Booking, Promocodes
from .serializers import BookingReadSerializer, BookingWriteSerializer
from promocodes.serializers import PromocodesSerializer
from django.utils import timezone

# Create your views here.

class BookingAPIView(APIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return BookingWriteSerializer
        return BookingReadSerializer

    def get(self, request, pk=None):
        if pk:
            booking_obj = get_object_or_404(Booking, pk=pk)
            serializer = BookingReadSerializer(booking_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        all_bookings = Booking.objects.all().order_by('-created_at')
        bookings = all_bookings.filter(deleted=False)
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
