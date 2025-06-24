from rest_framework import serializers
from services.models import Service
from bookings.models import Booking  
from django.contrib.auth import get_user_model
from properties.serializers import PropertySerializer
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
    owners = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    def get_owners(self, obj):
        return [
            {
                'id': owner.id,
                'name': owner.get_full_name() or owner.username,
                'slug': getattr(owner, 'slug', owner.username)
            }
            for owner in obj['owners']
        ]

    def get_properties(self, obj):
        return PropertySerializer(obj['properties'], many=True, context=self.context).data



