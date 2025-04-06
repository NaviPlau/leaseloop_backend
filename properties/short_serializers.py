from rest_framework import serializers
from .models import Property

class PropertyShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'name', 'address']
