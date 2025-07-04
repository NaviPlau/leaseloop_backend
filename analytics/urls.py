from django.urls import path
from .views import (
    BookingStatsView, 
    ServiceSalesView,
    RevenueGroupedByView,
    CancelledBookingsStatsView
)

urlpatterns = [
    path('bookings/', BookingStatsView.as_view()),
    path('services/', ServiceSalesView.as_view()),
    path('revenue-by/', RevenueGroupedByView.as_view()),
    path('cancelled-bookings/', CancelledBookingsStatsView.as_view()), 
]
