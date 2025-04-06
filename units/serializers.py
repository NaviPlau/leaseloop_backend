from rest_framework import serializers
from .models import Unit

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'property', 'name', 'description', 'capacity', 'price_per_night']
