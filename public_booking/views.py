from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from properties.models import Property
from public_booking.serializers import PublicOwnerBookingPageSerializer

User = get_user_model()

class PublicOwnerBookingPageView(APIView):
    def get(self, request, username):
        try:
            owner = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Owner not found'}, status=status.HTTP_404_NOT_FOUND)

        properties = Property.objects.filter(owner=owner, active=True, deleted=False)

        serializer = PublicOwnerBookingPageSerializer({
            'owner': owner,
            'properties': properties
        })
        return Response(serializer.data)
