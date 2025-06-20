from django.urls import path
from .views import ClientAPIView, PublicClientCreateAPIView

urlpatterns = [
    path('clients/', ClientAPIView.as_view()),
    path('client/<int:pk>/', ClientAPIView.as_view()),
    path('public/create-client/', PublicClientCreateAPIView.as_view(), name='public-create-client'),
]
