from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Promocodes
from .serializers import PromocodesSerializer
from utils.custom_pagination import CustomPageNumberPagination
# Create your views here.

class PromocodesAPIView(APIView):
    """
    API-Endpoint to manage promocodes.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            promocode_obj = get_object_or_404(Promocodes, pk=pk)
            serializer = PromocodesSerializer(promocode_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        promocodes = Promocodes.objects.filter(deleted=False).order_by('code')

        # ✅ Apply pagination only if 'page' is in query params
        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(promocodes, request)
            if page is not None:
                serializer = PromocodesSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        # ❌ No pagination → return all results
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
        promocode_obj.deleted = True
        promocode_obj.save()
        return Response({'message': 'Promocode successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)