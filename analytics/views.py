from rest_framework.views import APIView
from rest_framework.response import Response
from utils.custom_permission import IsOwnerOrAdmin
from django.db.models import Sum, Count
from bookings.models import Booking
from services.models import Service
from datetime import datetime
from django.utils.dateparse import parse_date
from collections import defaultdict
from properties.models import Property
from units.models import Unit
from django.db.models.functions import TruncYear, TruncMonth
from django.db.models import Q, Count
from django.utils.timezone import make_aware
from django.utils.timezone import is_naive

class RevenueGroupedByView(APIView):
    permission_classes = [IsOwnerOrAdmin]
    def get(self, request):
        """
        Returns a list of revenue grouped by unit or property

        Parameters:
            group_by (str): The field to group revenue by. Defaults to 'property'.
            from (str): The start date for the revenue range. Defaults to the earliest date if not provided.
            to (str): The end date for the revenue range. Defaults to the latest date if not provided.
            property (str): The ID of the property to filter revenue by. Defaults to 'all' if not provided.
            unit (str): The ID of the unit to filter revenue by. Defaults to 'all' if not provided.

        Returns:
            A list of dictionaries containing the name and revenue for each group.
        """
        group_by = request.GET.get('group_by', 'property')  
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        property_id = request.GET.get('property')
        unit_id = request.GET.get('unit')

        qs = Booking.objects.filter(check_in__lte=end_date, check_out__gte=start_date, status='confirmed')

        if property_id and property_id != 'all':
            qs = qs.filter(unit__property_id=property_id)
        if unit_id and unit_id != 'all':
            qs = qs.filter(unit_id=unit_id)

        if group_by == 'unit':
            qs = qs.values('unit__name').annotate(revenue=Sum('total_price')).order_by('unit__name')
            response_data = [{
                'name': item['unit__name'] or 'Unknown',
                'revenue': round(item['revenue'] or 0, 2)
            } for item in qs]
        else:
            qs = qs.values('property__name').annotate(revenue=Sum('total_price')).order_by('property__name')
            response_data = [{
                'name': item['property__name'] or 'Unknown',
                'revenue': round(item['revenue'] or 0, 2)
            } for item in qs]

        return Response(response_data)

class BookingStatsView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request):
        """
        Returns a dictionary of booking stats grouped by property and unit.

        Parameters:
            from (str): The start date for the booking range. Defaults to the earliest date if not provided.
            to (str): The end date for the booking range. Defaults to the latest date if not provided.
            property (str): The ID of the property to filter bookings by. Defaults to 'all' if not provided.
            unit (str): The ID of the unit to filter bookings by. Defaults to 'all' if not provided.

        Returns:
            A dictionary with the following structure:

            {
                'properties': {
                    '<property_id>': {
                        'name': '<property_name>',
                        'units': {
                            '<unit_id>': {
                                'pending': <count>,
                                'confirmed': <count>,
                                'total': <count>,
                                'name': '<unit_name>'
                            }
                        }
                    }
                }
            }
        """
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        property_id = request.GET.get('property')
        unit_id = request.GET.get('unit')

        bookings = Booking.objects.filter(check_in__lte=end_date, check_out__gte=start_date, status='confirmed')

        if property_id and property_id != 'all':
            bookings = bookings.filter(unit__property_id=property_id)
        if unit_id and unit_id != 'all':
            bookings = bookings.filter(unit_id=unit_id)

        stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for booking in bookings:
            pid = booking.unit.property_id
            uid = booking.unit_id
            status = booking.status

            stats[pid][uid][status] += 1
            stats[pid][uid]['total'] += 1

        result = {
            'properties': {
                str(pid): {
                    'name': Property.objects.get(id=pid).name,  
                    'units': {
                        str(uid): {
                            **unit_stats,
                            'name': Unit.objects.get(id=uid).name 
                        }
                        for uid, unit_stats in units.items()
                    }
                }
                for pid, units in stats.items()
            }
        }
        return Response(result)

class ServiceSalesView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request):
        """
        Returns a list of 5 most sold services of the given property/unit

        Parameters:
            from (str): The start date for the booking range. Defaults to the earliest date if not provided.
            to (str): The end date for the booking range. Defaults to the latest date if not provided.
            property (str): The ID of the property to filter bookings by. Defaults to 'all' if not provided.
            unit (str): The ID of the unit to filter bookings by. Defaults to 'all' if not provided.

        Returns:
            A list of dictionaries containing the name and sales of each service.
        """

        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))

        bookings_filter = {
            'bookings__check_in__lte': end_date,
            'bookings__check_out__gte': start_date
        }

        services = Service.objects.filter(**bookings_filter) \
            .annotate(sales_count=Count('bookings')) \
            .order_by('-sales_count')[:5]

        data = [{
            'name': service.name,
            'sales': service.sales_count
        } for service in services]

        return Response(data)

class CancelledBookingsStatsView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request):
        """
        Returns a JSON object containing the total and cancelled bookings count for each period, and cancellation rate.

        Parameters:
            from (str): The start date for the booking range. Defaults to the earliest date if not provided.
            to (str): The end date for the booking range. Defaults to the latest date if not provided.
            group_by (str): The period to group the bookings by. Defaults to 'year'. Options are 'year' and 'month'.
            property (str): The ID of the property to filter bookings by. Defaults to 'all' if not provided.
            unit (str): The ID of the unit to filter bookings by. Defaults to 'all' if not provided.

        Returns:
            A JSON object with the following structure:

            {
                'categories': [str, ...],
                'series': [
                    {
                        'name': str,
                        'type': str,
                        'data': [int, ...]
                    },
                    ...
                ]
            }
        """
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        group_by = request.GET.get('group_by', 'year')
        property_id = request.GET.get('property')
        unit_id = request.GET.get('unit')

        if not start_date or not end_date:
            return Response({'error': 'Missing date range.'}, status=400)

        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())

        if is_naive(start_date):
            start_date = make_aware(start_date)
        if is_naive(end_date):
            end_date = make_aware(end_date)

        bookings = Booking.objects.filter(check_in__range=(start_date, end_date))

        if property_id and property_id != 'all':
            bookings = bookings.filter(unit__property_id=property_id)
        if unit_id and unit_id != 'all':
            bookings = bookings.filter(unit_id=unit_id)

        if group_by == 'year':
            bookings = bookings.annotate(period=TruncYear('check_in'))
        else:
            bookings = bookings.annotate(period=TruncMonth('check_in'))

        grouped = bookings.values('period').annotate(
            total=Count('id'),
            cancelled=Count('id', filter=Q(status='cancelled'))
        ).order_by('period')

        categories = []
        total_data = []
        cancelled_data = []
        cancel_rate_data = []

        for entry in grouped:
            period = entry['period']
            period_key = period.strftime('%Y-%m') if group_by == 'month' else period.strftime('%Y')
            total = entry['total']
            cancelled = entry['cancelled']

            categories.append(period_key)
            total_data.append(total)
            cancelled_data.append(cancelled)
            cancel_rate_data.append(round((cancelled / total * 100) if total > 0 else 0, 2))

        return Response({
            'categories': categories,
            'series': [
                {
                    'name': 'Total Bookings',
                    'type': 'column',
                    'data': total_data
                },
                {
                    'name': 'Cancelled Bookings',
                    'type': 'column',
                    'data': cancelled_data
                },
                {
                    'name': 'Cancellation Rate (%)',
                    'type': 'line',
                    'data': cancel_rate_data
                }
            ]
        })
