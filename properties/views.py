from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Property , PropertyImage
from .serializers import PropertySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PropertyImageSerializer
from utils.custom_pagination import CustomPageNumberPagination
from utils.custom_permission import IsOwnerOrAdmin
from .filter import apply_property_filters


class PropertyAPIView(APIView):
    """
    API-Endpoint to manage properties.
    """
    permission_classes = [IsOwnerOrAdmin]
    def get(self, request, pk=None):
        """
        Gets a property or a list of all properties of the user.
        """
        if pk:
            property_obj = get_object_or_404(Property, pk=pk)

            if property_obj.owner != request.user:
                return Response(
                    {'error': 'Not authorized to see this property.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = PropertySerializer(property_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        properties = apply_property_filters(Property.objects.filter(owner=request.user, deleted=False), request)

        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(properties, request)
            if page is not None:
                serializer = PropertySerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        """
        Creates a new property image for the logged-in user.

        Args:
            request: The request object

        Returns:
            Response: The created property image in JSON format if the image was created successfully, otherwise the error messages in JSON format
        """
        serializer = PropertyImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Deletes a property image if the user is the owner.

        Args:
            request: The request object
            pk: The id of the image to delete

        Returns:
            Response: The message of successful deletion in JSON format if the image was deleted successfully, otherwise the error messages in JSON format
        """
        image = get_object_or_404(PropertyImage, pk=pk)

        if image.property.owner != request.user:
            return Response({'error': 'Not authorized to delete this image.'}, status=status.HTTP_403_FORBIDDEN)

        image.delete()
        return Response({'message': 'Image deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk):
        """
        Updates a property image if the user is the owner.

        Args:
            request: The request object containing the data to update the image.
            pk: The id of the property image to update.

        Returns:
            Response: The updated image in JSON format if the image was updated successfully, otherwise the error messages in JSON format.
        """

        image = get_object_or_404(PropertyImage, pk=pk)

        if image.property.owner != request.user:
            return Response({'error': 'Not authorized to edit this image.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PropertyImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)