from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    #TODO add userId field to serializer
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'created_at', 'updated_at']