from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .serializers import ClientSerializer
from .models import Client
from bookings .models import Booking
from django.db.models import Q
from utils.custom_pagination import CustomPageNumberPagination
from .filter import apply_client_filters



class ClientAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
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
        serializer = ClientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, pk=None):
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
    
class PublicClientCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        owner_id = request.data.get('owner_id')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        owner = None
        if owner_id:
            owner = get_object_or_404(User, id=owner_id)

        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=owner)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
