from django.contrib import admin
from django.utils.html import format_html

from .models import (
	PatientProfile,
	FileRecord,
	Comorbidity,
	PatientMedicalInfo,
	Doctor,
	PatientDoctorMapping,
)


class FileRecordInline(admin.StackedInline):
	model = FileRecord
	fk_name = 'patient'
	can_delete = False
	max_num = 1
	verbose_name = 'File Record'
	verbose_name_plural = 'File Record'
	readonly_fields = ('internal_file_number',)


class PatientMedicalInfoInline(admin.StackedInline):
	model = PatientMedicalInfo
	fk_name = 'patient'
	can_delete = False
	max_num = 1
	verbose_name = 'Medical Information'
	verbose_name_plural = 'Medical Information'
	filter_horizontal = ('comorbidities',)


class PatientDoctorMappingInline(admin.TabularInline):
	model = PatientDoctorMapping
	extra = 0
	fields = ('doctor', 'assigned_at', 'is_active')
	readonly_fields = ('assigned_at',)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
	list_display = (
		'full_name',
		'email',
		'contact_no',
		'type',
		'sex',
		'date_registered',
		'age',
		'internal_file',
	)
	search_fields = (
		'first_name',
		'last_name',
		'email',
		'contact_no',
		'file_record__internal_file_number',
		'file_record__external_file_number',
	)
	list_filter = ('type', 'sex', 'date_registered')
	ordering = ('-date_registered', 'last_name')
	readonly_fields = ('date_registered',)
	inlines = (FileRecordInline, PatientMedicalInfoInline, PatientDoctorMappingInline)
	fieldsets = (
		('Personal Information', {
			'fields': ('first_name', 'last_name', 'date_of_birth', 'sex')
		}),
		('Contact & Registration', {
			'fields': ('contact_no', 'email', 'type', 'created_by', 'date_registered')
		}),
	)
	autocomplete_fields = ('created_by',)

	def full_name(self, obj):
		return obj.get_full_name()
	full_name.short_description = 'Name'
	full_name.admin_order_field = 'last_name'

	def age(self, obj):
		return obj.get_age()
	age.short_description = 'Age'

	def internal_file(self, obj):
		if hasattr(obj, 'file_record') and obj.file_record:
			return obj.file_record.internal_file_number
		return '-'
	internal_file.short_description = 'Internal File'


@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
	list_display = ('internal_file_number', 'external_file_number', 'patient_link')
	search_fields = ('internal_file_number', 'external_file_number', 'patient__first_name', 'patient__last_name')
	readonly_fields = ('internal_file_number',)

	def patient_link(self, obj):
		if obj.patient_id:
			return format_html('<a href="/admin/core/app/patientprofile/{}/change/">{}</a>', obj.patient_id, obj.patient.get_full_name())
		return '-'
	patient_link.short_description = 'Patient'


@admin.register(Comorbidity)
class ComorbidityAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(PatientMedicalInfo)
class PatientMedicalInfoAdmin(admin.ModelAdmin):
	list_display = ('patient_link', 'blood_group', 'smokes', 'alcoholic')
	search_fields = ('patient__first_name', 'patient__last_name', 'patient__email')
	raw_id_fields = ('patient',)
	filter_horizontal = ('comorbidities',)

	def patient_link(self, obj):
		if obj.patient_id:
			return format_html('<a href="/admin/core/app/patientprofile/{}/change/">{}</a>', obj.patient_id, obj.patient.get_full_name())
		return '-'
	patient_link.short_description = 'Patient'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
	list_display = ('name', 'specialization', 'highest_qualification', 'years_of_experience', 'contact_no', 'email')
	search_fields = ('name', 'specialization', 'email', 'contact_no')
	list_filter = ('specialization',)


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
	list_display = ('patient_link', 'doctor_link', 'assigned_at', 'is_active')
	search_fields = ('patient__first_name', 'patient__last_name', 'doctor__name')
	list_filter = ('is_active', 'doctor')
	raw_id_fields = ('patient', 'doctor')

	def patient_link(self, obj):
		if obj.patient_id:
			return format_html('<a href="/admin/core/app/patientprofile/{}/change/">{}</a>', obj.patient_id, obj.patient.get_full_name())
		return '-'
	patient_link.short_description = 'Patient'

	def doctor_link(self, obj):
		if obj.doctor_id:
			return format_html('<a href="/admin/core/app/doctor/{}/change/">{}</a>', obj.doctor_id, obj.doctor.name)
		return '-'
	doctor_link.short_description = 'Doctor'

