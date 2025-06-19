from django.urls import path
from .views import PromocodesAPIView, ValidatePromocodeAPIView

urlpatterns = [
    path('promocodes/', PromocodesAPIView.as_view()),
    path('promocode/<int:pk>/', PromocodesAPIView.as_view()),
    path('public/promocode/validate/', ValidatePromocodeAPIView.as_view()),
]
