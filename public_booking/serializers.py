from rest_framework import serializers
from properties.models import Property
from units.models import Unit
from services.models import Service
from bookings.models import Booking  
from django.contrib.auth import get_user_model

User = get_user_model()


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    units = UnitSerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'name', 'description', 'address', 'units', 'services']


class PublicOwnerBookingPageSerializer(serializers.Serializer):
    owner = serializers.SerializerMethodField()
    properties = PropertySerializer(many=True)
    bookings = serializers.SerializerMethodField() 

    def get_owner(self, obj):
        owner = obj['owner']
        return {
            'id': owner.id,
            'name': owner.get_full_name() or owner.username,
            'slug': getattr(owner, 'slug', owner.username)
        }

    def get_bookings(self, obj):
        owner = obj['owner']
        unit_ids = Unit.objects.filter(property__owner=owner).values_list('id', flat=True)
        bookings = Booking.objects.filter(unit_id__in=unit_ids)
        return BookingSerializer(bookings, many=True).data
