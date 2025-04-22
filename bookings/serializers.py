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

    def create(self, validated_data):
    # Extract IDs from initial data
        service_ids = self.initial_data.get('services', [])
        unit_id = self.initial_data.get('unit')
        promo_code_id = self.initial_data.get('promo_code')

        check_in = validated_data.get('check_in')
        check_out = validated_data.get('check_out')
        guests_count = validated_data.get('guests_count')

        # Calculate total_days
        total_days = (check_out - check_in).days
        total_days = max(1, total_days)

        # Fetch Unit
        unit = Unit.objects.get(id=unit_id)
        validated_data['unit'] = unit
        validated_data['property'] = unit.property
        base_price = unit.price_per_night * total_days

        if guests_count > unit.max_capacity:
            extra_guests = guests_count - unit.capacity
            base_price += extra_guests * unit.price_per_extra_person * total_days

        # Fetch Services
        service_objs = Service.objects.filter(id__in=service_ids)
        total_services_price = 0.0
        for service in service_objs:
            if service.type == 'per_day':
                total_services_price += service.price * total_days
            else:
                total_services_price += service.price

        # Promo Code
        discount_amount = 0.0
        if promo_code_id:
            promo = Promocodes.objects.get(id=promo_code_id, active=True)
            validated_data['promo_code'] = promo
            discount_amount = (base_price + total_services_price) * (promo.discount_percent / 100)

        # Final price
        total_price = base_price + total_services_price - discount_amount

        # Add computed fields
        validated_data.update({
            'total_days': total_days,
            'base_renting_price': round(base_price, 2),
            'total_services_price': round(total_services_price, 2),
            'discount_amount': round(discount_amount, 2),
            'total_price': round(total_price, 2),
        })
        validated_data.pop('services', None)

        # Create booking without services
        booking = Booking.objects.create(**validated_data)

        # Set M2M services
        booking.services.set(service_objs)

        return booking
    
    def update(self, instance, validated_data):
        service_ids = self.initial_data.get('services', [])
        unit_id = self.initial_data.get('unit')
        promo_code_id = self.initial_data.get('promo_code')

        check_in = validated_data.get('check_in', instance.check_in)
        check_out = validated_data.get('check_out', instance.check_out)
        guests_count = validated_data.get('guests_count', instance.guests_count)

        
        total_days = (check_out - check_in).days
        total_days = max(1, total_days)

        
        unit = Unit.objects.get(id=unit_id) if unit_id else instance.unit
        validated_data['unit'] = unit
        base_price = unit.price_per_night * total_days

        if guests_count > unit.capacity:
            extra_guests = guests_count - unit.capacity 
            base_price += extra_guests * unit.price_per_extra_person * total_days

        
        service_objs = Service.objects.filter(id__in=service_ids)
        total_services_price = 0.0
        for service in service_objs:
            if service.type == 'per_day':
                total_services_price += service.price * total_days
            else:
                total_services_price += service.price

        discount_amount = 0.0
        if promo_code_id:
            promo = Promocodes.objects.get(id=promo_code_id, active=True)
            validated_data['promo_code'] = promo
            discount_amount = (base_price + total_services_price) * (promo.discount_percent / 100)

        total_price = base_price + total_services_price - discount_amount
        validated_data.update({
            'total_days': total_days,
            'base_renting_price': round(base_price, 2),
            'total_services_price': round(total_services_price, 2),
            'discount_amount': round(discount_amount, 2),
            'total_price': round(total_price, 2),
        })

        validated_data.pop('services', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        instance.services.set(service_objs)

        return instance

class BookingReadSerializer(serializers.ModelSerializer):
        property = PropertySerializer(source='unit.property', read_only=True)
        unit = UnitSerializer()
        client = ClientSerializer()
        promo_code = PromocodesSerializer()
        services = ServiceSerializer(many=True)

        class Meta:
            model = Booking
            fields = '__all__'