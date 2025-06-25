from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from properties.models import Property
from public_booking.serializers import PublicOwnerBookingPageSerializer
from django.utils.dateparse import parse_date
from units.models import Unit
from bookings.models import Booking
from units.serializers import UnitSerializer
from django.core.paginator import Paginator, EmptyPage
User = get_user_model()

class PublicOwnerBookingPageView(APIView):
    def get(self, request):
        """
        Gets a list of properties with their owners and pagination information.

        Args:
            request (Request): The request object.

        Returns:
            Response: The response object with the properties and pagination information.

        Raises:
            Exception: If an error occurs while retrieving the properties or pagination information.
        """
        try:
            city = request.query_params.get("city")
            country = request.query_params.get("country")

            filters = {"active": True, "deleted": False}
            if city:
                filters["address__city__iexact"] = city
            if country:
                filters["address__country__iexact"] = country

            all_properties = Property.objects.filter(**filters).order_by('id')

            page_number = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)
            paginator = Paginator(all_properties, page_size)

            try:
                properties_page = paginator.page(page_number)
            except EmptyPage:
                return Response({'detail': 'Page out of range'}, status=status.HTTP_404_NOT_FOUND)

            owners = User.objects.filter(id__in=[prop.owner.id for prop in properties_page])

            serializer = PublicOwnerBookingPageSerializer(
                {'owners': owners, 'properties': properties_page},
                context={'request': request}
            )

            return Response({
                'pagination': {
                    'page': int(page_number),
                    'page_size': int(page_size),
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count
                },
                'data': serializer.data
            })

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AvailableUnitsView(APIView):
    def get(self, request):
        """
        GET /public/bookings/available-units

        Returns a list of available units for the given date range and guest count.

        query parameters:
        - check_in: date of check-in
        - check_out: date of check-out
        - guests: number of guests

        Returns 200 OK with a list of UnitSerializer objects if successful.
        Returns 400 BAD REQUEST if the request body does not contain the required data or if the date range is invalid.
        """
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        guest_count = request.query_params.get('guests', 1)

        try:
            check_in_date = parse_date(check_in)
            check_out_date = parse_date(check_out)
            guest_count = int(guest_count)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid date or guest count'}, status=status.HTTP_400_BAD_REQUEST)

        if not check_in_date or not check_out_date or check_in_date >= check_out_date:
            return Response({'error': 'Invalid date range'}, status=status.HTTP_400_BAD_REQUEST)

        units = Unit.objects.filter(active=True, max_capacity__gte=guest_count, property__active=True, property__deleted=False)

        available_units = []
        for unit in units:
            overlapping_bookings = Booking.objects.filter(
                unit=unit,
                status__in=['pending', 'confirmed'],
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            )
            if not overlapping_bookings.exists():
                available_units.append(unit)

        serializer = UnitSerializer(available_units, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
