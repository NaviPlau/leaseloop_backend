from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from bookings.models import Booking
from units.models import Unit
from .serializers import DashboardStatsSerializer

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Gets the dashboard statistics.

        Returns a JSON object with the following statistics:

        - next_arrival: The date of the next arrival.
        - next_departure: The date of the next departure.
        - guests_present: The number of guests currently present.
        - occupancy_today: The percentage of occupancy for today.
        - occupancy_month: The percentage of occupancy for the month.

        :param request: The request object
        :return: A JSON object with the dashboard statistics
        """
        user = request.user

        try:
            units = Unit.objects.filter(property__owner=user)
            bookings = Booking.objects.filter(unit__property__owner=user)

            if not units.exists():
                return Response({"error": "No units found for this user."}, status=status.HTTP_404_NOT_FOUND)

            if not bookings.exists():
                return Response({"error": "No bookings found for this user."}, status=status.HTTP_404_NOT_FOUND)

            today = timezone.now().date()

            # Next arrival
            upcoming_arrivals = bookings.filter(check_in__gte=today).order_by("check_in")
            next_arrival = upcoming_arrivals.first().check_in if upcoming_arrivals.exists() else None

            # Next departure
            upcoming_departures = bookings.filter(check_out__gte=today).order_by("check_out")
            next_departure = upcoming_departures.first().check_out if upcoming_departures.exists() else None

            # Guests currently present
            active_guests = bookings.filter(check_in__lte=today, check_out__gte=today)
            guests_total = sum([b.guests_count for b in active_guests])

            # Occupancy today
            units_total = units.count()
            occupied_today = bookings.filter(check_in__lte=today, check_out__gt=today).count()
            occupancy_today = round((occupied_today / units_total) * 100) if units_total > 0 else 0

            # Monthly occupancy
            start_of_month = today.replace(day=1)
            end_of_month = timezone.datetime(today.year, today.month + 1, 1).date() if today.month < 12 else timezone.datetime(today.year + 1, 1, 1).date()
            total_available_nights = units_total * (end_of_month - start_of_month).days

            occupied_nights = 0
            for booking in bookings:
                check_in = booking.check_in
                check_out = booking.check_out

                start = max(check_in, start_of_month)
                end = min(check_out, end_of_month)

                delta = (end - start).days
                if delta > 0:
                    occupied_nights += delta

            occupancy_month = round((occupied_nights / total_available_nights) * 100) if total_available_nights > 0 else 0

            response_data = {
                "next_arrival": next_arrival,
                "next_departure": next_departure,
                "guests_present": guests_total,
                "occupancy_today": occupancy_today,
                "occupancy_month": occupancy_month
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        return Response({"error": "POST method not allowed on this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request):
        return Response({"error": "PUT method not allowed on this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request):
        return Response({"error": "DELETE method not allowed on this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
