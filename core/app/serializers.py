from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer #type:ignore
from rest_framework_simplejwt.tokens import RefreshToken #type:ignore

from .models import PatientProfile

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
		)
		read_only_fields = ("id", "date_registered", "age")

	def get_age(self, obj):
		return obj.get_age()

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

