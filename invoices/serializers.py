from rest_framework import serializers
from .models import Invoice
from bookings.serializers import BookingReadSerializer

class InvoiceSerializer(serializers.ModelSerializer):
    booking = BookingReadSerializer(read_only=True)
    class Meta:
        model = Invoice
        fields = '__all__'
