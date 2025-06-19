from django.urls import path
from .views import ServiceAPIView, PublicServiceListByProperty

urlpatterns = [
    path('services/', ServiceAPIView.as_view()),
    path('service/<int:pk>/', ServiceAPIView.as_view()),
    path('public/services/', PublicServiceListByProperty.as_view(), name='public-service-list'),
]
