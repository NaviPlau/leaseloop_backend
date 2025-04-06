from rest_framework import serializers
from .models import Unit
from properties.models import Property
from properties.short_serializers import PropertyShortSerializer

class UnitSerializer(serializers.ModelSerializer):
    property = PropertyShortSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), write_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'property', 'property_id', 'name', 'description', 'capacity', 'price_per_night'
        ]