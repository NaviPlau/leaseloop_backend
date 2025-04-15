from rest_framework import serializers
from .models import Booking, Promocodes
from clients.models import Client
from services.models import Service
from units.models import Unit
from clients.serializers import ClientSerializer
from units.serializers import UnitSerializer
from services.serializers import ServiceSerializer
from promocodes.serializers import PromocodesSerializer
from properties.serializers import PropertySerializer

from invoices.models import Invoice
from invoices.utils import generate_invoice_pdf

class BookingWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = '__all__'

    # def create(self, validated_data):
    #     services_data = validated_data.pop('services', [])

    #     booking = Booking.objects.create(**validated_data)

    #     booking.services.set(services_data)

    #     # Total services price calculation
    #     total_services_price = 0
    #     for service in services_data:
    #         if service.type == 'per_day':
    #             total_services_price += service.price * booking.guests_count * booking.total_days
    #         else:
    #             total_services_price += service.price

    #     booking.total_services_price = total_services_price

    #     if booking.promo_code:
    #         booking.discount_amount = (booking.base_renting_price * (booking.promo_code.discount_percent / 100))

    #     booking.total_price = booking.base_renting_price + booking.total_services_price - booking.discount_amount

    #     booking.save()

    #     if not hasattr(self, 'invoice'):
    #         invoice = Invoice.objects.create(
    #             booking=self,
    #             deposit_paid=self.deposit_paid,
    #             deposit_amount=self.deposit_amount,
    #             rental_price=self.base_renting_price,
    #             rental_days=self.total_days,
    #             services_price=self.total_services_price,
    #             total_price=self.total_price,
    #             promo_code=self.promo_code.code if self.promo_code else None,
    #             discount_amount=self.discount_amount,
    #         )
    #         generate_invoice_pdf(invoice)
            
    #     return booking

class BookingReadSerializer(serializers.ModelSerializer):
        property = PropertySerializer()
        unit = UnitSerializer()
        client = ClientSerializer()
        promo_code = PromocodesSerializer()
        services = ServiceSerializer(many=True)

        class Meta:
            model = Booking
            fields = '__all__'