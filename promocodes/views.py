from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Promocodes
from .serializers import PromocodesSerializer
from utils.custom_pagination import CustomPageNumberPagination
from utils.custom_permission import IsOwnerOrAdmin
from .filter import apply_promocode_filters
from datetime import date

class PromocodesAPIView(APIView):
    """
    API-Endpoint to manage promocodes.
    """
    permission_classes = [IsOwnerOrAdmin]
    def get(self, request, pk=None):
        if pk:
            promocode_obj = get_object_or_404(Promocodes, pk=pk)
            self.check_object_permissions(request, promocode_obj)
            serializer = PromocodesSerializer(promocode_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        promocodes = Promocodes.objects.filter(deleted=False)
        if not request.user.is_staff:
            promocodes = promocodes.filter(owner_id=request.user)
        promocodes = apply_promocode_filters(promocodes, request)
        if 'page' in request.query_params:
            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(promocodes, request)
            if page is not None:
                serializer = PromocodesSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

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
    
    
class ValidatePromocodeAPIView(APIView):
    authentication_classes = [] 
    permission_classes = []     

    def post(self, request):
        """
        Validate a promo code for a specific owner.

        This API endpoint takes a POST request with the following fields:
        - code (string): The promo code to validate.
        - owner_id (int): The ID of the owner associated with the promo code.

        Returns:
            Response: A JSON response with the following keys:
            - valid (bool): Indicates whether the promo code is valid.
            - discount_percent (float): The discount percentage of the promo code, if valid.
            - description (string): A description of the promo code, if valid.
            - valid_until (date): The expiry date of the promo code, if valid.
            - error (string): An error message if the promo code is invalid.

        Returns HTTP 200 if the promo code is valid, HTTP 400 if the promo code is expired
        or if code and owner_id are not provided, and HTTP 404 if the promo code is not found
        or inactive.
        """
        code = request.data.get("code", "").strip()
        owner_id = request.data.get("owner_id")
        if not code or not owner_id:
            return Response({"valid": False, "error": "Code and owner_id required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            promo = Promocodes.objects.get(
                code__iexact=code,
                owner_id=owner_id,
                deleted=False,
                active=True
            )
        except Promocodes.DoesNotExist:
            return Response({"valid": False, "error": "Code not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        if promo.valid_until < date.today():
            return Response({"valid": False, "error": "Promo code expired."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "id" : promo.id,
            "valid": True,
            "discount_percent": promo.discount_percent,
            "description": promo.description,
            "valid_until": promo.valid_until
        }, status=status.HTTP_200_OK)