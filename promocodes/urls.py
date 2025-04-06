from django.urls import path
from .views import PromocodesAPIView

urlpatterns = [
    path('promocodes/', PromocodesAPIView.as_view()),
    path('promocode/<int:pk>/', PromocodesAPIView.as_view()),
]
