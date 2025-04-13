from django.urls import path
from .views import reset_guest_demo_data

urlpatterns = [
    path('demo-init/', reset_guest_demo_data, name='initialize-guest-demo'),
]