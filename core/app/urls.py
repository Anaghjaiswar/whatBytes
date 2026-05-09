from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterAPIView, LoginAPIView

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='auth_register'),
    path('auth/login/', LoginAPIView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
