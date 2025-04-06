from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Booking, Promocodes
from .serializers import BookingSerializer
from promocodes.serializers import PromocodesSerializer
from django.utils import timezone

# Create your views here.

class BookingAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            booking_obj = get_object_or_404(Booking, pk=pk)
            serializer = BookingSerializer(booking_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # List all bookings
        bookings = Booking.objects.all().order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk=None):
        if not pk:
            return Response({'error': 'Booking-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)

        booking_obj = get_object_or_404(Booking, pk=pk)
        serializer = BookingSerializer(booking_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': 'Booking-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)

        booking_obj = get_object_or_404(Booking, pk=pk)
        booking_obj.delete()
        return Response({'message': 'Booking successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)    
