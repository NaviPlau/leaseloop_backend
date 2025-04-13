from django.urls import path
from .views import generate_invoice

urlpatterns = [
    path('generate/<int:booking_id>/', generate_invoice, name='generate-invoice'),
]
