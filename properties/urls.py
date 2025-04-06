from django.urls import path
from .views import PropertyAPIView, PropertyImageUploadView

urlpatterns = [
    path('properties/', PropertyAPIView.as_view()),
    path('properties/<int:pk>/', PropertyAPIView.as_view()),
    path('property-images/', PropertyImageUploadView.as_view(), name='property-image-upload'),
]
