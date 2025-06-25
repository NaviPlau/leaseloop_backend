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
        """
        Creates a new unit instance.

        This method takes validated data, creates a new unit instance from it, and
        then assigns the provided property and amenities to the unit.

        :param validated_data: A dictionary containing the validated data for
        creating a new unit. It should include keys like 'name', 'description',
        'price_per_night', 'max_capacity', 'property_id', 'amenities'.
        :return: The newly created unit instance.
        """
        property_obj = validated_data.pop('property_id')
        amenities_data = validated_data.pop('amenities', [])
        unit = Unit.objects.create(property=property_obj, **validated_data)
        unit.amenities.set(amenities_data)
        return unit
    
    def update(self, instance, validated_data):
        """
        Updates an existing unit instance with validated data.

        This method takes the validated data, updates the unit instance with the
        provided data, and then assigns the provided amenities to the unit.

        :param instance: The existing unit instance to be updated.
        :param validated_data: A dictionary containing the validated data for
        updating the unit. It may include keys like 'name', 'description',
        'price_per_night', 'max_capacity', 'amenities', 'active', 'type', and
        'status'.
        :return: The updated unit instance.
        """
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
        """
        Returns the URL of the first image of the unit if it exists, otherwise returns None.

        This method is used to build the URL of the first image of the unit based on the
        request object. If the request object is not None, it appends the request's base URL
        to the image's relative URL. If the request object is None, it returns the image's
        relative URL as is.

        :param obj: The unit object for which the image URL is being generated.
        :return: The URL of the first image of the unit if it exists, otherwise None.
        """
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None
    

