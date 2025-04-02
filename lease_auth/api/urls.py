from django.urls import path
from lease_auth.api import views

urlpatterns = [
  path('register/', views.RegistrationView.as_view(), name='register'),
]