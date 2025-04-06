from rest_framework import serializers
from .models import Booking, Promocodes
from clients.models import Client
from services.models import Service
from clients.serializers import ClientSerializer
from units.serializers import UnitSerializer
from services.serializers import ServiceSerializer
class BookingSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    services = ServiceSerializer(read_only=True, many=True)
    class Meta:
        model = Booking
        fields = [
            'id', 'unit', 'client', 'check_in', 'check_out', 'guests', 'total_price',
            'deposit_paid', 'deposit_amount', 'status', 'services', 'promo_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['unit', 'client', 'created_at', 'updated_at', 'services', 'promo_code']