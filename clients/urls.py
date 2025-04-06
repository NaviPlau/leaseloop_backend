from django.urls import path
from .views import ClientAPIView

urlpatterns = [
    path('clients/', ClientAPIView.as_view()),
    path('clients/<int:pk>/', ClientAPIView.as_view()),
]
