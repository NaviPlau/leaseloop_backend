from rest_framework import serializers
from .models import Promocodes

class PromocodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocodes
        fields = '__all__'