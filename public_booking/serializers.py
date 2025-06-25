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
        """
        Returns a list of dictionaries containing the owner id, name and slug of
        every owner in the obj['owners'] list.

        Args:
            obj (dict): A dictionary with the key 'owners' containing a list of owners

        Returns:
            list: A list of dictionaries containing the owner id, name and slug
        """
        return [
            {
                'id': owner.id,
                'name': owner.get_full_name() or owner.username,
                'slug': getattr(owner, 'slug', owner.username)
            }
            for owner in obj['owners']
        ]

    def get_properties(self, obj):
        """
        Returns a list of PropertySerializer objects for every property in the
        obj['properties'] list.

        Args:
            obj (dict): A dictionary with the key 'properties' containing a list of
            properties

        Returns:
            list: A list of PropertySerializer objects
        """
        return PropertySerializer(obj['properties'], many=True, context=self.context).data



