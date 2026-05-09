from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PatientProfile, Doctor

from .serializers import (
	RegisterSerializer,
	CustomTokenObtainPairSerializer,
	UserSerializer,
	PatientProfileSerializer,
	DoctorSerializer,
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


class PatientListCreateAPIView(generics.ListCreateAPIView):
	serializer_class = PatientProfileSerializer
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		return PatientProfile.objects.filter(created_by=self.request.user).order_by("-date_registered")

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = PatientProfileSerializer
	permission_classes = (IsAuthenticated,)
	lookup_field = "id"
	lookup_url_kwarg = "id"

	def get_queryset(self):
		return PatientProfile.objects.filter(created_by=self.request.user)


class DoctorListCreateAPIView(generics.ListCreateAPIView):
	serializer_class = DoctorSerializer
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		return Doctor.objects.all().order_by("name")

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)


class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = DoctorSerializer
	permission_classes = (IsAuthenticated,)
	lookup_field = "id"
	lookup_url_kwarg = "id"

	def get_queryset(self):
		return Doctor.objects.all()

