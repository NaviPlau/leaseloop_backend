from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .serializers import ClientSerializer
from .models import Client
# Create your views here.
class ClientAPIView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request, pk=None):
        if pk:
            client_obj = get_object_or_404(Client, pk=pk)
            
            if client_obj.userId != request.user:
                return Response(
                    {'error': 'Not authorized to see this client.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = ClientSerializer(client_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # List all clients of the user
        clients = Client.objects.filter(userId=request.user).order_by('-created_at')
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(userId=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, pk=None):
        if not pk:
            return Response({'error': 'Client-ID requeried.'}, status=status.HTTP_400_BAD_REQUEST)
        
        client_obj = get_object_or_404(Client, pk=pk)
        
        if client_obj.userId != request.user:
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
        
        if client_obj.userId != request.user:
            return Response(
                {'error': 'Not authorized to delete this client.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        client_obj.delete()
        return Response({'message': 'Client successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)