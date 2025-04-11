from rest_framework import serializers
from .models import Unit, UnitImage
from properties.models import Property
from properties.short_serializers import PropertyShortSerializer

class UnitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitImage
        fields = ['id', 'image', 'alt_text', 'unit', 'created_at', 'updated_at']

class UnitSerializer(serializers.ModelSerializer):
    property = PropertyShortSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), write_only=True)
    images = UnitImageSerializer(many=True, read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'property', 'property_id', 'name', 'description', 'max_capacity', 'price_per_extra_person', 'capacity', 'price_per_night', 'status', 'images'
        ]

    def create(self, validated_data):
        property_obj = validated_data.pop('property_id')
        unit = Unit.objects.create(property=property_obj, **validated_data)
        return unit