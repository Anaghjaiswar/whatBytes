from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterAPIView,
    LoginAPIView,
    PatientListCreateAPIView,
    PatientDetailAPIView,
    DoctorListCreateAPIView,
    DoctorDetailAPIView,
     MappingListCreateAPIView,
     MappingByPatientOrDeleteAPIView,
)

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='auth_register'),
    path('auth/login/', LoginAPIView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('patients/', PatientListCreateAPIView.as_view(), name='patient_list_create'),
    path('patients/<int:id>/', PatientDetailAPIView.as_view(), name='patient_detail'),
    path('doctors/', DoctorListCreateAPIView.as_view(), name='doctor_list_create'),
    path('doctors/<int:id>/', DoctorDetailAPIView.as_view(), name='doctor_detail'),
     path('mappings/', MappingListCreateAPIView.as_view(), name='mapping_list_create'),
     path('mappings/<int:patient_id>/', MappingByPatientOrDeleteAPIView.as_view(), name='mapping_by_patient_or_delete'),
]
