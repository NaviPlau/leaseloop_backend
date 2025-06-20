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
        address_data = validated_data.pop('address', None)
        if address_data:
            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()
        return super().update(instance, validated_data)
