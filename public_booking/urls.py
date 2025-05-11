from django.urls import path
from .views import PublicOwnerBookingPageView, AvailableUnitsView

urlpatterns = [
    path("booking/", PublicOwnerBookingPageView.as_view(), name="public-booking"),
    path('booking/available-units/', AvailableUnitsView.as_view()),
    
]
