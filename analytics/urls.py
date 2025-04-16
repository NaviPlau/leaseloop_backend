from django.urls import path
from .views import (
    RevenueOverviewView, 
    BookingStatsView, 
    CancellationStatsView,
    ServiceSalesView,
    TopBookingPeriodsView,
    RevenueGroupedByView,
)

urlpatterns = [
    path('revenue/', RevenueOverviewView.as_view()),
    path('bookings/', BookingStatsView.as_view()),
    path('cancellations/', CancellationStatsView.as_view()),
    path('services/', ServiceSalesView.as_view()),
    path('booking-periods/', TopBookingPeriodsView.as_view()),
    path('revenue-by/', RevenueGroupedByView.as_view()),  # ?group_by=property&range=monthly
]
