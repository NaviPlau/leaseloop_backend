from rest_framework import serializers
from addresses.serializers import AddressSerializer
from addresses.models import Address
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Creates a new client instance.

        It takes validated data and creates a new instance of Client model. It
        also creates a new instance of Address model and assigns it to the
        client's address field.

        :param validated_data: A dictionary containing the validated data for
        creating a new client. It should include keys like 'user', 'first_name',
        'last_name', 'email', 'address'.
        :return: The newly created client instance.
        """
        user = validated_data.pop('user', None) 
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        client = Client.objects.create(
            **validated_data,
            address=address,
            user=user 
        )
        return client
    
    def update(self, instance, validated_data):
        """
        Updates an existing client instance with validated data.

        It takes validated data and updates the client instance with it. If the
        validated data contains a key 'address', it updates the client's address
        instance with the provided address data.

        :param instance: The existing client instance to be updated.
        :param validated_data: A dictionary containing the validated data for
        updating the client. It may include keys like 'first_name', 'last_name',
        'email', 'address'.
        :return: The updated client instance.
        """
        address_data = validated_data.pop('address', None)
        if address_data:
            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()
        return super().update(instance, validated_data)
