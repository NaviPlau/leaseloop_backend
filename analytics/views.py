from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from bookings.models import Booking
from services.models import Service
from datetime import datetime
from django.utils.dateparse import parse_date

class RevenueOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))

        qs = Booking.objects.filter(created_at__range=(start_date, end_date), status='confirmed')
        revenue = qs.aggregate(total=Sum('total_price'))
        return Response({'total_revenue': revenue['total'] or 0})


class BookingStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        bookings = Booking.objects.filter(created_at__range=(start_date, end_date))
        return Response({
            'total': bookings.count(),
            'new': bookings.filter(status='confirmed').count()
        })


class CancellationStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        canceled = Booking.objects.filter(status='cancelled', updated_at__range=(start_date, end_date)).count()
        return Response({'cancellations': canceled})


class ServiceSalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))
        services = Service.objects.filter(bookings__created_at__range=(start_date, end_date)) \
            .annotate(sales_count=Count('bookings')) \
            .order_by('-sales_count')[:5]

        data = [{
            'name': service.name,
            'sales': service.sales_count
        } for service in services]

        return Response(data)


class TopBookingPeriodsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Booking.objects.extra(select={'day': "date(created_at)"}).values('day').annotate(count=Count('id')).order_by('-count')[:7]
        return Response(qs)


class RevenueGroupedByView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_by = request.GET.get('group_by', 'property')
        start_date = parse_date(request.GET.get('from'))
        end_date = parse_date(request.GET.get('to'))

        if group_by == 'unit':
            qs = Booking.objects.filter(created_at__range=(start_date, end_date)) \
                .values('unit__name') \
                .annotate(revenue=Sum('total_price'))
        else:  # default: property
            qs = Booking.objects.filter(created_at__range=(start_date, end_date)) \
                .values('property__name') \
                .annotate(revenue=Sum('total_price'))

        return Response(qs)
