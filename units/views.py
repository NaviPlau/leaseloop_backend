from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Unit, UnitImage
from properties.models import Property
from .serializers import UnitSerializer, UnitImageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

class UnitAPIView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request, pk=None, property_id=None):
        """
        Gets a unit or a list of all units of the user.

        Args:
            request: The request object
            pk: The id of the unit to get
            property_id: The id of the property to get the units of

        Returns:
            Response: The unit or the list of units in JSON format
        """
        if pk:
            unit = get_object_or_404(Unit, pk=pk)
            return Response(UnitSerializer(unit).data, status=status.HTTP_200_OK)

        if property_id:
            units = Unit.objects.filter(property_id=property_id)
            return Response(UnitSerializer(units, many=True).data, status=status.HTTP_200_OK)

        units = Unit.objects.all()
        return Response(UnitSerializer(units, many=True).data, status=status.HTTP_200_OK)

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

        unit.status = 'unavailable'
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