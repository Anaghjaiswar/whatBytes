from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
	RegisterSerializer,
	CustomTokenObtainPairSerializer,
	UserSerializer,
)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	permission_classes = (AllowAny,)

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		refresh = RefreshToken.for_user(user)
		data = {
			"user": UserSerializer(user).data,
			"refresh": str(refresh),
			"access": str(refresh.access_token),
		}
		return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):
	permission_classes = (AllowAny,)
	serializer_class = CustomTokenObtainPairSerializer

