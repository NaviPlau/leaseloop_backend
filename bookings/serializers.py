from rest_framework import serializers
from .models import Booking, Promocodes
from clients.models import Client
from services.models import Service
from units.models import Unit
from clients.serializers import ClientSerializer
from units.serializers import UnitSerializer
from services.serializers import ServiceSerializer
from promocodes.serializers import PromocodesSerializer
class BookingSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Service.objects.all()
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all()
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all()
    )

    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        services_data = validated_data.pop('services', [])

        booking = Booking.objects.create(**validated_data)

        booking.services.set(services_data)

        # Total services price calculation
        total_services_price = 0
        for service in services_data:
            if service.type == 'per_day':
                total_services_price += service.price * booking.guests_count * booking.total_days
            else:
                total_services_price += service.price

        booking.total_services_price = total_services_price

        if booking.promo_code:
            booking.discount_amount = (booking.base_renting_price * (booking.promo_code.discount_percent / 100))

        booking.total_price = booking.base_renting_price + booking.total_services_price - booking.discount_amount

        booking.save()

        return booking