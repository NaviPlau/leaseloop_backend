from django.urls import path
from lease_auth.api import views

urlpatterns = [
  path('register/', views.RegistrationView.as_view(), name='register'),
  path('login/', views.LoginView.as_view(), name='login'),
  path('activate-account/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate-account'),
]