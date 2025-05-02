from django.urls import path
from lease_auth.api import views

urlpatterns = [
  path('register/', views.RegistrationView.as_view(), name='register'),
  path('login/', views.LoginView.as_view(), name='login'),
  path('activate-account/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate-account'),
  path('reset-password/<str:token>/', views.PasswordResetView.as_view(), name='password_reset'),
  path('forgot-password/', views.ForgotPasswordView.as_view(), name='password_reset'),
  path('remember-login/', views.TokenLoginView.as_view(), name='token_login'),


  path('logo/', views.LogoView.as_view()),
  path('logo/<int:pk>/', views.LogoView.as_view()),
  path('change-password/', views.ChangePasswordView.as_view()),
  path('change-email/', views.ChangeEmailView.as_view()),
  path('change-personals/', views.ChangeProfileDataView.as_view()),
  path('get-full-user-data/', views.GetFullUserDataView.as_view()),
]