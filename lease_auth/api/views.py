from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from lease_auth.api.serializers import RegistrationSerializer, LogoSerializer, ChangePasswordSerializer, ChangeEmailSerializer, ChangeProfileDataSerializer, GetFullUserDataSerializer
from rest_framework import status
from lease_auth.api.utils import send_welcome_email, send_password_reset_email, clean_expired_tokens, send_changed_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from lease_auth.models import User
from lease_auth.models import PasswordResetToken , LoginToken, UserLogo, Profile

import uuid

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
        clean_expired_tokens()
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
                'message': 'You registered successfully! Please check your email to activate your account. Otherwise, you can not log in.',
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
        clean_expired_tokens()
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
        

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user using email and password.
        """
        clean_expired_tokens()
        username = request.data.get('email')  
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response({"message": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_active:
                return Response({"message": "You still didn't activate your account."}, status=status.HTTP_403_FORBIDDEN)

            token = str(uuid.uuid4())
            LoginToken.objects.create(user=user, token=token)

            return Response(
                {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "token": token, "email": user.email},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response({"message": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
        


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Send a password reset email to the user.

        This API endpoint takes a POST request with the following field:
        - email (string): The email address of the user.

        Returns a JSON response with the following key:
        - message (string): A message indicating that the password reset email was sent successfully.

        The endpoint returns HTTP 200 if the email is sent successfully.
        """
        clean_expired_tokens()
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4()) 
            PasswordResetToken.objects.create(user=user, token=token)
            reset_link = f"https://lease-loop.com/reset-password/{token}/"
            send_password_reset_email(
                user_email=user.email,
                user_name=user.username,
                reset_link=reset_link
            )
            return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
        

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Confirm and set a new password for the user using a password reset token.

        This API endpoint takes a POST request with the following fields:
        - password (string): The new password for the user.
        - repeated_password (string): The repeated password for confirmation.

        The endpoint checks if the provided token is valid and not expired, 
        then sets the new password for the user if the token is valid and 
        both password fields match.

        Returns a JSON response with the following keys:
        - message (string): A message indicating that the password was reset successfully.
        - error (string): An error message if the token is invalid or expired, or if 
        the password fields are missing or do not match.

        The endpoint returns HTTP 200 if the password is reset successfully, and HTTP 400 
        if there is an error.
        """
        clean_expired_tokens()
        token = kwargs.get('token')
        password = request.data.get('password')
        repeated_password = request.data.get('repeated_password')
        if not password or not repeated_password:
            return Response({'error': 'Both password fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        if password != repeated_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid():
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            user = reset_token.user
            user.set_password(password)
            user.save()
            reset_token.delete()
            return Response({'message': 'Password reset successfully!'}, status=status.HTTP_200_OK)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        

class TokenLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
        Authenticate a user using the authentication token.

        This API endpoint takes a POST request with the following field:
        - token (string): The authentication token of the user.

        Returns a JSON response with the following keys:
        - id (int): The ID of the user.
        - email (string): The email address of the user.
        - token (string): The authentication token of the user.

        The endpoint returns HTTP 200 if the authentication is successful, and HTTP 401 if the token is invalid.
        """
        clean_expired_tokens()
        token = request.data.get('token')
        try:
            login_token = LoginToken.objects.get(token=token)
            if not login_token.is_valid():
                login_token.delete()
                return Response({"message": "Token has expired. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

            user = login_token.user
            return Response({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "token": login_token.token,
                "email": user.email
            }, status=status.HTTP_200_OK)
        except LoginToken.DoesNotExist:
            return Response({"message": "Token has expired. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)
        

class LogoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        logo = UserLogo.objects.filter(user=user).first()
        serializer = LogoSerializer(logo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        user = request.user
        logo = UserLogo.objects.filter(user=user).first()
        serializer = LogoSerializer(logo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user

        serializer = ChangeEmailSerializer(user, data=request.data)
        if serializer.is_valid():
            new_email = serializer.validated_data['new_email']
            send_changed_email(user.email, user.first_name, new_email)
            serializer.save()
            return Response({"detail": "Email changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangeProfileDataView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ChangeProfileDataSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetFullUserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = GetFullUserDataSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)