from django.urls import path
from .views import PropertyAPIView

urlpatterns = [
    path('properties/', PropertyAPIView.as_view()),
    path('properties/<int:pk>/', PropertyAPIView.as_view()),
]
