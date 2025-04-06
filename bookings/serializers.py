from rest_framework import serializers
from .models import Booking, Promocodes
from clients.models import Client
from services.models import Service

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'unit', 'client', 'check_in', 'check_out', 'guests', 'total_price', 'deposit_paid', 'deposit_amount', 'status', 'services', 'promo_code', 'created_at', 'updated_at']