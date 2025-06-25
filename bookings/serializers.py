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

class BookingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        """
        Creates a booking and calculates the total price of the booking.
        
        It takes into account the unit's price per night, the number of guests, the number of days, any extra guests, and the services selected. If a promotional code is provided, it also applies the discount to the total price.
        
        :returns: The created booking.
        """
        service_ids = self.initial_data.get('services', [])
        unit_id = self.initial_data.get('unit')
        promo_code_id = self.initial_data.get('promo_code')
        client_id = self.initial_data.get('client')
        if client_id:
            client = Client.objects.get(id=client_id)
            validated_data['client'] = client
        check_in = validated_data.get('check_in')
        check_out = validated_data.get('check_out')
        guests_count = validated_data.get('guests_count')
        total_days = (check_out - check_in).days
        total_days = max(1, total_days)
        unit = Unit.objects.get(id=unit_id)
        validated_data['unit'] = unit
        validated_data['property'] = unit.property
        base_price = unit.price_per_night * total_days
        if guests_count > unit.max_capacity:
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
        booking = Booking.objects.create(**validated_data)
        booking.services.set(service_objs)
        return booking
    
    def update(self, instance, validated_data):
        """
        Update an existing booking instance with validated data.

        This method updates the booking instance with new details such as check-in,
        check-out dates, number of guests, unit, services, and promo code. It also 
        recalculates the total days, base renting price, total services price, discount 
        amount, and total price based on the provided data.

        Parameters:
        - instance: The existing booking instance to be updated.
        - validated_data: A dictionary containing the validated data for updating 
        the booking. It may include keys like 'check_in', 'check_out', 
        'guests_count', 'unit', 'services', and 'promo_code'.

        Returns:
        - The updated booking instance.
        """
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