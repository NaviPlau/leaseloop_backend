from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from lease_auth.api.serializers import RegistrationSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from lease_auth.api.utils import send_welcome_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from lease_auth.models import User

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        This API endpoint takes a POST request with the following fields:
        - email (string): The email address of the user.
        - password (string): The password to use for the user.
        - repeated_password (string): The repeated password to check against the password.
        Returns a JSON response with the following keys:
        - message (string): A message indicating that the user was registered successfully.
        - user_id (int): The ID of the user that was just registered.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))  
            token = default_token_generator.make_token(user) 
            send_welcome_email(
                user_email=user.email,
                user_name=user.username,
                activation_link=f"https://lease-loop.com/activate-account/{uid}/{token}/"
            )
            return Response({
                'message': 'You registered successfully',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token, *args, **kwargs):
        """
        Activate a user's account using the activation link.

        This API endpoint takes a GET request with the following parameters:
        - uidb64 (string): The base64-encoded user ID.
        - token (string): The activation token.

        Returns a JSON response with the following keys:
        - message (string): A message indicating that the account was activated successfully.
        - error (string): An error message if the activation link is invalid or has expired, or if the user is invalid.

        The endpoint returns HTTP 200 if the account is activated successfully, and HTTP 400 if there is an error.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True 
                user.save()
                return Response({"message": "Account activated successfully! You can now log in."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Activation link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)