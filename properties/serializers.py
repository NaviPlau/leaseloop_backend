from rest_framework import serializers
from .models import Property, PropertyImage
from units.serializers import UnitSerializer

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'alt_text', 'property', 'created_at', 'updated_at']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    units = UnitSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'name', 'address', 'description',
            'created_at', 'updated_at', 'images', 'units'
        ]
        read_only_fields = ['owner']


