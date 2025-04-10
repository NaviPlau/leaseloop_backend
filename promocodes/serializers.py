from rest_framework import serializers
from .models import Promocodes

class PromocodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocodes
        fields = '__all__'
        read_only_fields = ['owner_id', 'created_at', 'updated_at']