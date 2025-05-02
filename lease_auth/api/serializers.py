from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from ..models import UserLogo, Profile
from addresses.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'house_number', 'postal_code', 'city', 'country', 'phone']


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d])[^\s]{8,}$',
                message="Min. 8 chars. Min. one uppercase, one number and one special character"
            )
        ]
    )
    
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
    
    def validate(self, data):
        """
        Validate the registration data.

        This method checks if the provided email is already registered 
        and ensures that the password and repeated password match.

        Args:
            data (dict): The registration data containing 'email', 
                        'password', and 'repeated_password'.

        Raises:
            serializers.ValidationError: If the email already exists 
                                        or if the passwords do not match.

        Returns:
            dict: The validated data.
        """

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"detail": "Please retry with other data"})
        
        return data
    
    def create(self, validated_data):
        """
        Create a new user with the validated data.

        This method takes the validated registration data, removes the repeated
        password, sets the username to the email, and creates a new user with
        the remaining data. The user is set to inactive and saved.

        Args:
            validated_data (dict): The validated registration data

        Returns:
            User: The newly created user
        """
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        user.is_active = False 
        user.save()
        return user
    

class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLogo
        fields = ('id', 'logo', 'user')


class ChangePasswordSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'confirm_password')

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.instance

        # Check if old password is correct
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"detail": "Old password is incorrect."})

        # Check if new passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"detail": "Passwords must match."})

        return data
    
    def save(self):
        user = self.instance  # this is the user object passed in the view
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class ChangeEmailSerializer(serializers.Serializer):
    actual_email = serializers.EmailField(write_only=True)
    new_email = serializers.EmailField(write_only=True)
    actual_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('actual_email', 'new_email', 'actual_password')

    def validate(self, data):
        user = self.instance
        if not user.check_password(data['actual_password']):
            raise serializers.ValidationError({"detail": "Actual password is incorrect."})
        
        if user.email != data['actual_email']:
            raise serializers.ValidationError({"detail": "Actual email is incorrect."})

        return data
    
    def save(self):
        user = self.instance 
        user.email = self.validated_data['new_email']
        user.username = self.validated_data['new_email']
        user.save()
        return user


class ChangeProfileDataSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = Profile
        fields = ['tax_id', 'address', 'first_name', 'last_name']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        address_data = validated_data.pop('address', None)

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update user fields
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Handle address create or update
        if address_data:
            if instance.address:
                for attr, value in address_data.items():
                    setattr(instance.address, attr, value)
                instance.address.save()
            else:
                address = Address.objects.create(**address_data)
                instance.address = address

        instance.data_filled = True
        instance.save()
        return instance
    

class GetFullUserDataSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    tax_id = serializers.CharField()
    data_filled = serializers.BooleanField()
    address = AddressSerializer(allow_null=True)
    image = LogoSerializer(allow_null=True)

    def to_representation(self, user):
        # Ensure profile exists
        profile = getattr(user, 'profile', None)
        logo = UserLogo.objects.filter(user=user).first()
        
        if not profile:
            profile = Profile.objects.create(user=user)

        print(f"Profile Address: {profile.address}")

        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tax_id': profile.tax_id,
            'data_filled': profile.data_filled,
            'address': AddressSerializer(profile.address).data if profile.address else None,
            'image': LogoSerializer(logo).data if logo else None
        }