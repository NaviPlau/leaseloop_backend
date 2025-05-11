from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .utils import send_contact_email



class ContactAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    user = request.user
    user_email = user.username
    user_name = user.first_name + ' ' + user.last_name
    theme = request.data.get('theme')
    message = request.data.get('message')

    send_contact_email(user_email, user_name, message, theme)

    return Response({'success': 'Email sent successfully.'}, status=status.HTTP_200_OK)

