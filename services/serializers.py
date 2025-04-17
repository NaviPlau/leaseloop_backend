from rest_framework import serializers
from .models import Service
from properties.models import Property
from properties.short_serializers import PropertyShortSerializer


class ServiceSerializer(serializers.ModelSerializer):
    property_info = PropertyShortSerializer(source='property', read_only=True)
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())


    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'type', 'property', 'property_info', 'created_at', 'updated_at', 'active']

