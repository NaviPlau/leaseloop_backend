from django.urls import path
from .views import BookingAPIView, PublicBookingCreateAPIView

urlpatterns = [
    path('bookings/', BookingAPIView.as_view()),
    path('booking/<int:pk>/', BookingAPIView.as_view()),
    path('public/create-booking/', PublicBookingCreateAPIView.as_view(), name='public-create-booking'),
]
