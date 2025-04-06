from rest_framework import serializers
from .models import Property, PropertyImage

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'altText', 'created_at', 'updated_at']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'name', 'address', 'description',
            'created_at', 'updated_at', 'images'
        ]
        read_only_fields = ['owner']


