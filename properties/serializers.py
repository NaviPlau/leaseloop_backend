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
        """
        Creates a new property instance.

        This method takes the validated data, creates an Address instance with
        the provided address data, assigns the logged-in user as the owner, and
        then creates a new Property instance with the remaining data.

        :param validated_data: A dictionary containing the validated data for
        creating a new property. It should include keys like 'address', 'name',
        'description', etc.
        :return: The newly created property instance.
        """

        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        user = self.context['request'].user
        validated_data['owner'] = user
        return Property.objects.create(address=address, **validated_data)

    def update(self, instance, validated_data):
        """
        Updates an existing property instance with validated data.

        This method takes the validated data, updates the property's address
        instance with the provided address data, and then updates the property
        instance with the remaining data.

        :param instance: The existing property instance to be updated.
        :param validated_data: A dictionary containing the validated data for
        updating the property. It may include keys like 'address', 'name',
        'description', etc.
        :return: The updated property instance.
        """
        address_data = validated_data.pop('address', None)
        if address_data:
            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()
        return super().update(instance, validated_data)
    
    def get_image_url(self, obj):
        """
        Returns the URL of the first image of the property if it exists, otherwise returns None.

        This method is used to build the URL of the first image of the property based on the
        request object. If the request object is not None, it appends the request's base URL
        to the image's relative URL. If the request object is None, it returns the image's
        relative URL as is.

        :param obj: The property object for which the image URL is being generated.
        :return: The URL of the first image of the property if it exists, otherwise None.
        """
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None    
