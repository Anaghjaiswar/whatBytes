from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView #type:ignore
from rest_framework_simplejwt.tokens import RefreshToken #type:ignore
from .models import PatientProfile, Doctor, PatientDoctorMapping 

from .serializers import (
	RegisterSerializer,
	CustomTokenObtainPairSerializer,
	UserSerializer,
	PatientProfileSerializer,
	DoctorSerializer,
	PatientDoctorMappingSerializer,
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


class MappingListCreateAPIView(generics.ListCreateAPIView):
	serializer_class = PatientDoctorMappingSerializer
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		return PatientDoctorMapping.objects.select_related("patient", "doctor").order_by("-assigned_at")


class MappingByPatientOrDeleteAPIView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request, patient_id):
		get_object_or_404(PatientProfile, id=patient_id)
		mappings = PatientDoctorMapping.objects.filter(patient_id=patient_id).select_related("patient", "doctor").order_by("-assigned_at")
		serializer = PatientDoctorMappingSerializer(mappings, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def delete(self, request, patient_id):
		mapping = get_object_or_404(PatientDoctorMapping, id=patient_id)
		mapping.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

