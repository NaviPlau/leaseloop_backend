from rest_framework import serializers
from properties.models import Property
from units.models import Unit
from services.models import Service
from bookings.models import Booking  
from django.contrib.auth import get_user_model
from properties.serializers import PropertySerializer
from units.serializers import UnitSerializer 

User = get_user_model()


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = 'check_in', 'check_out', 'status', 'unit'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class PublicOwnerBookingPageSerializer(serializers.Serializer):
    owner = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()

    def get_owner(self, obj):
        owner = obj['owner']
        return {
            'id': owner.id,
            'name': owner.get_full_name() or owner.username,
            'slug': getattr(owner, 'slug', owner.username)
        }

    def get_properties(self, obj):
        properties = obj['properties']
        return PropertySerializer(properties, many=True, context=self.context).data

    def get_bookings(self, obj):
        owner = obj['owner']
        unit_ids = Unit.objects.filter(property__owner=owner).values_list('id', flat=True)
        bookings = Booking.objects.filter(unit_id__in=unit_ids)
        return BookingSerializer(bookings, many=True).data
