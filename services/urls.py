from django.urls import path
from .views import ServiceAPIView

urlpatterns = [
    path('services/', ServiceAPIView.as_view()),
    path('service/<int:pk>/', ServiceAPIView.as_view()),
]
