from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from bookings.models import Booking
from services.models import Service
from datetime import datetime
from django.utils.dateparse import parse_date
from collections import defaultdict

class RevenueGroupedByView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_by = request.GET.get('group_by', 'property')  
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        property_id = request.GET.get('property')
        unit_id = request.GET.get('unit')

        qs = Booking.objects.filter(created_at__range=(start_date, end_date), status='confirmed')

        if property_id and property_id != 'all':
            qs = qs.filter(property_id=property_id)
        if unit_id and unit_id != 'all':
            qs = qs.filter(unit_id=unit_id)

        if group_by == 'unit':
            qs = qs.values('unit__name').annotate(revenue=Sum('total_price')).order_by('unit__name')
            response_data = [{
                'name': item['unit__name'],
                'revenue': item['revenue'] or 0
            } for item in qs]
        else:
            qs = qs.values('property__name').annotate(revenue=Sum('total_price')).order_by('property__name')
            response_data = [{
                'name': item['property__name'],
                'revenue': item['revenue'] or 0
            } for item in qs]

        return Response(response_data)


class BookingStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        property_id = request.GET.get('property')
        unit_id = request.GET.get('unit')

        bookings = Booking.objects.filter(created_at__range=(start_date, end_date))

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
                    'units': {
                        str(uid): dict(unit_stats)
                        for uid, unit_stats in units.items()
                    }
                }
                for pid, units in stats.items()
            }
        }

        return Response(result)




class ServiceSalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        property_id = request.GET.get('property')
        unit_id = request.GET.get('unit')

        bookings_filter = {'bookings__created_at__range': (start_date, end_date)}
        if property_id and property_id != 'all':
            bookings_filter['bookings__property_id'] = property_id
        if unit_id and unit_id != 'all':
            bookings_filter['bookings__unit_id'] = unit_id

        services = Service.objects.filter(**bookings_filter) \
            .annotate(sales_count=Count('bookings')) \
            .order_by('-sales_count')[:5]

        data = [{
            'name': service.name,
            'sales': service.sales_count
        } for service in services]

        return Response(data)


