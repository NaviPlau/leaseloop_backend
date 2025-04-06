from django.urls import path
from .views import UnitAPIView

urlpatterns = [
    path('units/', UnitAPIView.as_view()),
    path('units/<int:pk>/', UnitAPIView.as_view()),
    path('properties/<int:property_id>/units/', UnitAPIView.as_view()),
]
