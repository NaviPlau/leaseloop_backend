from django.urls import path
from .views import PublicOwnerBookingPageView

urlpatterns = [
    path("booking/<slug:username>/", PublicOwnerBookingPageView.as_view(), name="public-booking")
]
