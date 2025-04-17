from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Promocodes
from .serializers import PromocodesSerializer
from django.utils import timezone
# Create your views here.

class PromocodesAPIView(APIView):
    """
    API-Endpoint to manage promocodes.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        """
        Gets a promocode or a list of all promocodes.
        """
        if pk:
            # Fetch the specific promocode by its ID
            promocode_obj = get_object_or_404(Promocodes, pk=pk)
            serializer = PromocodesSerializer(promocode_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # List all promocodes
        promocodes = Promocodes.objects.all().order_by('-created_at')
        serializer = PromocodesSerializer(promocodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creates a new promocode.
        """
        serializer = PromocodesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk=None):
        """
        Updates a promocode.
        """
        if not pk:
            return Response({'error': 'Promocode-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)

        promocode_obj = get_object_or_404(Promocodes, pk=pk)
        serializer = PromocodesSerializer(promocode_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """
        Deletes a promocode.
        """
        if not pk:
            return Response({'error': 'Promocode-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)

        promocode_obj = get_object_or_404(Promocodes, pk=pk)
        promocode_obj.active = False
        promocode_obj.save()
        return Response({'message': 'Promocode successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)