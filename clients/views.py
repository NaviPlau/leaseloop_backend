from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .serializers import ClientSerializer
from .models import Client
from bookings .models import Booking
from utils.custom_pagination import CustomPageNumberPagination
from .filter import apply_client_filters
from rest_framework import generics
from django.contrib.auth import get_user_model

class ClientAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk=None):
        """
        If pk is provided, returns a client object with the given id.
        If the client does not exist or the user is not authorized to see it, returns a 404 or 403 status code respectively.

        If no pk is provided, returns a list of all clients that the user has created.
        The list is paginated. If the 'page' parameter is provided in the query parameters, the list is paginated with the given page number.
        Otherwise, the list is not paginated.
        """
        if pk:
            client_obj = get_object_or_404(Client, pk=pk)
            if client_obj.user != request.user:
                return Response(
                    {'error': 'Not authorized to see this client.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = ClientSerializer(client_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        clients = apply_client_filters(Client.objects.filter(user=request.user, deleted=False), request)
        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(clients, request)
            if page is not None:
                serializer = ClientSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        """
        Creates a new client.
        """
        
        serializer = ClientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, pk=None):
        """
        Updates a client if the user is the owner.

        Args:
            request: The request object
            pk: The id of the client to update

        Returns:
            Response: The client in JSON format if the client was updated successfully, otherwise the error messages in JSON format
        """
        if not pk:
            return Response({'error': 'Client-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)
        client_obj = get_object_or_404(Client, pk=pk) 
        if client_obj.user != request.user:
            return Response(
                {'error': 'Not authorized to edit this client.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ClientSerializer(client_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk=None):
        """
        Deletes a client if the user is the owner.

        Args:
            request: The request object
            pk: The id of the client to delete

        Returns:
            Response: The message of successful deletion in JSON format if the client was deleted successfully, otherwise the error messages in JSON format
        """
        if not pk:
            return Response({'error': 'Client-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)
        client_obj = get_object_or_404(Client, pk=pk)
        if client_obj.user != request.user:
            return Response(
                {'error': 'Not authorized to delete this client.'},
                status=status.HTTP_403_FORBIDDEN
            )
        bookings = Booking.objects.filter(client=client_obj)
        for booking in bookings:
            booking.status = 'cancelled'
            booking.save()
        client_obj.deleted = True
        client_obj.save()
        return Response({'message': 'Client successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)
    
class PublicClientCreateAPIView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        """
        Creates a new client.

        Args:
            request: The request object
            *args: Any additional arguments
            **kwargs: Any additional keyword arguments

        Returns:
            Response: The newly created client in JSON format if the client was created successfully, otherwise the error messages in JSON format
        """
        owner_id = request.data.get('owner_id')
        User = get_user_model()
        if not owner_id:
            return Response({'error': 'owner_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        owner = get_object_or_404(User, id=owner_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=owner)
        return Response({
            'message': 'Client successfully created',
            'client': serializer.data
        }, status=status.HTTP_201_CREATED)
