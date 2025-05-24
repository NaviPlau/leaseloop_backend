from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Service
from properties.models import Property
from .serializers import ServiceSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from utils.custom_pagination import CustomPageNumberPagination

class ServiceAPIView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request, pk=None, property_id=None):
        """
        Gets a service or a list of all services of the property.
        """
        if pk:
            service_obj = get_object_or_404(Service, pk=pk)

            if service_obj.property.owner != request.user:
                return Response(
                    {'error': 'Not authorized to see this service.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ServiceSerializer(service_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # List all services of the user
        services = Service.objects.filter(property__owner=request.user, deleted=False).order_by('-created_at')

        # ✅ Only apply pagination if ?page is provided
        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(services, request)
            if page is not None:
                serializer = ServiceSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        # ❌ Return all services without pagination
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        """
        Creates a new service for the logged-in owner.

        Args:
            request: The request object

        Returns:
            Response: The created service in JSON format if the service was created successfully, otherwise the error messages in JSON format
        """
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            property_id = serializer.validated_data['property'].id
            if Property.objects.filter(id=property_id, owner=request.user).exists():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": " Not autorisiert to create service for this property."}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk=None):
        """
        Updates a service if the user is the owner.

        Args:
            request: The request object
            pk: The id of the service to update

        Returns:
            Response: The service in JSON format if the service was updated successfully, otherwise the error messages in JSON format
        """
        if not pk:
            return Response({"error": "Service-ID requiered."}, status=status.HTTP_400_BAD_REQUEST)
        service = get_object_or_404(Service, pk=pk)
        if service.property.owner != request.user:
            return Response({"error": "Not authorized to edit this service."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """
        Deletes a service if the user is the owner.

        Args:
            request: The request object
            pk: The id of the service to delete

        Returns:
            Response: The deleted service in JSON format if the service was deleted successfully, otherwise the error messages in JSON format
        """
        if not pk:
            return Response({"error": "Service-ID requiered."}, status=status.HTTP_400_BAD_REQUEST)
        service = get_object_or_404(Service, pk=pk)
        if service.property.owner != request.user:
            return Response({"error": "Not authorized to delete this service."}, status=status.HTTP_403_FORBIDDEN)
        service.deleted = True
        service.save()
        return Response({"message": f"Service {pk} successfully deleted."}, status=status.HTTP_204_NO_CONTENT)