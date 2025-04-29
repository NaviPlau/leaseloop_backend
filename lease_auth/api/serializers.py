from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from ..models import UserLogo


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