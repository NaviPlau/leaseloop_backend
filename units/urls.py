from django.urls import path
from .views import UnitAPIView, UnitImageView, AmenityListAPIView

urlpatterns = [
    path('units/', UnitAPIView.as_view()),
    path('units/<int:pk>/', UnitAPIView.as_view()),
    path('properties/<int:property_id>/units/', UnitAPIView.as_view()),
    path('unit-images/', UnitImageView.as_view(), name='unit-image-upload'),
    path('unit-image/<int:pk>/', UnitImageView.as_view(), name='unit-image-delete'),
    path('amenities/', AmenityListAPIView.as_view(), name='amenity-list'),
]
