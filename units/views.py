from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Unit, UnitImage, Amenity
from properties.models import Property
from .serializers import UnitSerializer, UnitImageSerializer, AmenitySerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from utils.custom_pagination import CustomPageNumberPagination
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import CharField
from utils.custom_permission import IsOwnerOrAdmin

class UnitAPIView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request, pk=None, property_id=None):
        if pk:
            unit = get_object_or_404(Unit, pk=pk)
            self.check_object_permissions(request, unit)
            return Response(UnitSerializer(unit).data, status=status.HTTP_200_OK)
        if property_id:
            units = Unit.objects.filter(property_id=property_id, deleted=False)
        else:
            units = Unit.objects.filter(deleted=False)

        if not request.user.is_staff:
            units = units.filter(property__owner=request.user)

        search = request.query_params.get('search')
        if search:
            units = units.annotate(
                max_capacity_str=Cast('max_capacity', CharField())
            ).filter(
                Q(name__icontains=search) |
                Q(property__name__icontains=search) |
                Q(max_capacity_str__icontains=search) |
                Q(status__icontains=search) | 
                Q(description__icontains=search)
            )

        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            paginated_units = paginator.paginate_queryset(units, request)
            if paginated_units is not None:
                serialized = UnitSerializer(paginated_units, many=True)
                return paginator.get_paginated_response(serialized.data)

        serialized = UnitSerializer(units, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creates a new unit for the logged-in user.

        Args:
            request: The request object

        Returns:
            Response: The created unit in JSON format if the unit was created successfully, otherwise the error messages in JSON format
        """
        serializer = UnitSerializer(data=request.data)
        if serializer.is_valid():
            property_id = serializer.validated_data['property_id'].id
            if Property.objects.filter(id=property_id, owner=request.user).exists():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": "Not authorized to create unit for this property."}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """
        Updates a unit if the user is the owner.

        Args:
            request: The request object
            pk: The id of the unit to update

        Returns:
            Response: The unit in JSON format if the unit was updated successfully, otherwise the error messages in JSON format
        """
        if not pk:
            return Response({"error": "Unit-ID requiered."}, status=status.HTTP_400_BAD_REQUEST)
        unit = get_object_or_404(Unit, pk=pk)
        if unit.property.owner != request.user:
            return Response({"error": "Not authorized to edit this unit."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UnitSerializer(unit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Deletes a unit if the user is the owner.

        Args:
            request: The request object
            pk: The id of the unit to delete

        Returns:
            Response: The message of successful deletion in JSON format if the unit was deleted successfully, otherwise the error messages in JSON format
        """
        if not pk:
            return Response({"error": "Unit-ID required."}, status=status.HTTP_400_BAD_REQUEST)
        unit = get_object_or_404(Unit, pk=pk)
        if unit.property.owner != request.user:
            return Response({"error": "Not authorized to delete this unit."}, status=status.HTTP_403_FORBIDDEN)

        unit.deleted= True
        unit.save()
        return Response({"message": f"Unit {pk} successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


class UnitImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = UnitImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        image = get_object_or_404(UnitImage, pk=pk)
        
        if image.unit.property.owner!= request.user:
            return Response({'error': 'Not authorized to delete this image.'}, status=status.HTTP_403_FORBIDDEN)

        image.delete()
        return Response({'message': 'Image deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk):
        image = get_object_or_404(UnitImage, pk=pk)
        
        if image.unit.property.owner != request.user:
            return Response({'error': 'Not authorized to edit this image.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UnitImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AmenityListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        amenities = Amenity.objects.all()
        serializer = AmenitySerializer(amenities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)