from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .models import Property , PropertyImage
from .serializers import PropertySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PropertyImageSerializer


class PropertyAPIView(APIView):
    """
    API-Endpoint to manage properties.
    """

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
        properties = properties.filter(deleted=False)	
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format = None):
        """
        Creates a new property for the logged-in user.
        """
        serializer = PropertySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None, format = None):
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

        serializer = PropertySerializer(property_obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format = None):
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

        property_obj.deleted = True
        property_obj.save()
        return Response({'message': 'Property successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)


class PropertyImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = PropertyImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        image = get_object_or_404(PropertyImage, pk=pk)

        # Optional: check ownership
        if image.property.owner != request.user:
            return Response({'error': 'Not authorized to delete this image.'}, status=status.HTTP_403_FORBIDDEN)

        image.delete()
        return Response({'message': 'Image deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk):
        image = get_object_or_404(PropertyImage, pk=pk)

        # Optional: check ownership
        if image.property.owner != request.user:
            return Response({'error': 'Not authorized to edit this image.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PropertyImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)