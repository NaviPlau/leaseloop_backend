from rest_framework import serializers
from .models import Property, PropertyImage
from units.serializers import UnitSerializer
from addresses.models import Address
from addresses.serializers import AddressSerializer

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'alt_text', 'property', 'created_at', 'updated_at']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    units = UnitSerializer(many=True, read_only=True)
    address = AddressSerializer()
    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'name', 'address', 'description',
            'created_at', 'updated_at', 'images', 'units', 'active', 'email'  ]
        read_only_fields = ['owner']


    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        user = self.context['request'].user
        validated_data['owner'] = user
        return Property.objects.create(address=address, **validated_data)

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()
        return super().update(instance, validated_data)
    
    def get_image_url(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None    
