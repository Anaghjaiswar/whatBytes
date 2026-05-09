from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer #type:ignore
from rest_framework_simplejwt.tokens import RefreshToken #type:ignore

from .models import PatientProfile, Doctor, PatientDoctorMapping

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ("id", "username", "email", "first_name", "last_name")
		read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(write_only=True, required=True)
	last_name = serializers.CharField(write_only=True, required=True)
	password = serializers.CharField(write_only=True, min_length=8)

	class Meta:
		model = User
		fields = ("id", "first_name","last_name", "email", "password")
		read_only_fields = ("id",)

	def validate_email(self, value):
		if User.objects.filter(email__iexact=value).exists():
			raise serializers.ValidationError("A user with this email already exists.")
		return value

	@transaction.atomic
	def create(self, validated_data):
		first_name = validated_data.pop("first_name")
		last_name = validated_data.pop("last_name")
		email = validated_data.pop("email")
		password = validated_data.pop("password")

		# create user; use email as username to simplify
		user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
		return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token["email"] = user.email
		return token

	def validate(self, attrs):
		data = super().validate(attrs)
		data["user"] = UserSerializer(self.user).data
		return data


class PatientProfileSerializer(serializers.ModelSerializer):
	age = serializers.SerializerMethodField(read_only=True)
	file_record = serializers.SerializerMethodField(read_only=True)
	created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

	class Meta:
		model = PatientProfile
		fields = (
			"id",
			"first_name",
			"last_name",
			"date_of_birth",
			"sex",
			"contact_no",
			"email",
			"type",
			"date_registered",
			"created_by",
			"age",
			"file_record",
		)
		read_only_fields = ("id", "date_registered", "age", "file_record")

	def get_age(self, obj):
		return obj.get_age()

	def get_file_record(self, obj):
		file_record = getattr(obj, "file_record", None)
		if not file_record:
			return None
		return {
			"internal_file_number": file_record.internal_file_number,
			"external_file_number": file_record.external_file_number,
		}

	def validate_date_of_birth(self, value):
		if value > date.today():
			raise serializers.ValidationError("Date of birth cannot be in the future.")
		return value

	def validate_email(self, value):
		queryset = PatientProfile.objects.filter(email__iexact=value)
		if self.instance:
			queryset = queryset.exclude(pk=self.instance.pk)
		if queryset.exists():
			raise serializers.ValidationError("A patient with this email already exists.")
		return value


class DoctorSerializer(serializers.ModelSerializer):
	created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

	class Meta:
		model = Doctor
		fields = (
			"id",
			"name",
			"contact_no",
			"email",
			"highest_qualification",
			"specialization",
			"years_of_experience",
			"created_by",
		)
		read_only_fields = ("id",)

	def validate_years_of_experience(self, value):
		if value < 0:
			raise serializers.ValidationError("Years of experience cannot be negative.")
		return value

	def validate_email(self, value):
		queryset = Doctor.objects.filter(email__iexact=value)
		if self.instance:
			queryset = queryset.exclude(pk=self.instance.pk)
		if queryset.exists():
			raise serializers.ValidationError("A doctor with this email already exists.")
		return value


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
	patient = serializers.PrimaryKeyRelatedField(queryset=PatientProfile.objects.all())
	doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
	patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)
	doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)

	class Meta:
		model = PatientDoctorMapping
		fields = (
			"id",
			"patient",
			"doctor",
			"patient_name",
			"doctor_name",
			"assigned_at",
			"is_active",
		)
		read_only_fields = ("id", "assigned_at", "is_active", "patient_name", "doctor_name")

	def validate(self, attrs):
		patient = attrs.get("patient")
		doctor = attrs.get("doctor")
		if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
			raise serializers.ValidationError("This doctor is already assigned to this patient.")
		return attrs

