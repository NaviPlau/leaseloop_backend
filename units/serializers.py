from rest_framework import serializers
from .models import Unit, UnitImage, Amenity
from properties.models import Property
from properties.short_serializers import PropertyShortSerializer

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'
        
class UnitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitImage
        fields = ['id', 'image', 'alt_text', 'unit', 'created_at', 'updated_at']

class UnitSerializer(serializers.ModelSerializer):
    property = PropertyShortSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), write_only=True)
    images = UnitImageSerializer(many=True, read_only=True)
    amenities = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), many=True, required=False)
    amenity_details = AmenitySerializer(source='amenities', many=True, read_only=True)

    
    class Meta:
        model = Unit
        fields = '__all__'
        extra_fields = ['amenities_ids']

    def create(self, validated_data):
        property_obj = validated_data.pop('property_id')
        amenities_data = validated_data.pop('amenities', [])
        unit = Unit.objects.create(property=property_obj, **validated_data)
        unit.amenities.set(amenities_data)
        return unit
    
    def update(self, instance, validated_data):
        amenities_data = validated_data.pop('amenities', None)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.max_capacity = validated_data.get('max_capacity', instance.max_capacity)
        instance.price_per_extra_person = validated_data.get('price_per_extra_person', instance.price_per_extra_person)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.price_per_night = validated_data.get('price_per_night', instance.price_per_night)
        instance.status = validated_data.get('status', instance.status)
        instance.type = validated_data.get('type', instance.type)
        instance.active = validated_data.get('active', instance.active)
        instance.save()
        if amenities_data is not None:                    
            instance.amenities.set(amenities_data)        
        return instance
    
    def get_image_url(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None
    

