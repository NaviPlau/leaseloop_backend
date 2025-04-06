from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .models import Property
from .serializers import PropertySerializer


class PropertyAPIView(APIView):
    """
    API-Endpoint to manage properties.
    """

    #authentication_classes = [TokenAuthentication]
    #permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request, pk=None):
        """
        Gets a property or a list of all properties of the user.
        """
        if pk:
            property_obj = get_object_or_404(Property, pk=pk)

            if property_obj.owner != request.user:
                return Response(
                    {'error': 'Not authorized, to see this property.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = PropertySerializer(property_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # List all properties of the user
        properties = Property.objects.filter(owner=request.user).order_by('-created_at')
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creates a new property for the logged-in user.
        """
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """
        Updates a property if the user is the owner.
        """
        if not pk:
            return Response({'error': 'Property-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)

        property_obj = get_object_or_404(Property, pk=pk)

        if property_obj.owner != request.user:
            return Response(
                {'error': 'Not authorized to edit this property.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PropertySerializer(property_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Deletes a property if the user is the owner.
        """
        if not pk:
            return Response({'error': 'Property-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)

        property_obj = get_object_or_404(Property, pk=pk)

        if property_obj.owner != request.user:
            return Response(
                {'error': 'Not authorized to delete this property.'},
                status=status.HTTP_403_FORBIDDEN
            )

        property_obj.delete()
        return Response({'message': 'Property successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)
