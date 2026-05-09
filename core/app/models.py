from django.db import models
from datetime import date
from django.core.validators import RegexValidator
from django.conf import settings
from django.db import transaction



phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)



class PatientProfile(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Free', 'Free'),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registered_patients'
    )

    first_name = models.CharField(max_length=255, help_text="First name of the patient", verbose_name="First Name")
    last_name = models.CharField(max_length=255, help_text="Last name of the patient", verbose_name="Last Name")    
    date_of_birth = models.DateField(help_text="Date of birth of the patient", verbose_name="Date of Birth")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, help_text="Sex of the patient", verbose_name="Sex")
    contact_no = models.CharField(max_length=20, validators=[phone_validator], help_text="Contact number of the patient", verbose_name="Contact Number")
    email = models.EmailField(help_text="Email address of the patient", verbose_name="Email Address",unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, help_text="Type of the patient", verbose_name="Type")
    date_registered = models.DateField(auto_now_add=True, help_text="Date when the patient was registered", verbose_name="Date Registered") 

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.type}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age
    

class FileRecord(models.Model):
    """Patient ke liye unique folder/file record tracking"""
    patient = models.OneToOneField(
        PatientProfile, 
        on_delete=models.CASCADE, 
        related_name='file_record'
    )
    internal_file_number = models.CharField(max_length=30, unique=True, editable=False)
    external_file_number = models.CharField(max_length=30, unique=True, blank=True, null=True)

    def __str__(self):
        return f"File: {self.internal_file_number} for {self.patient.get_full_name()}"
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.internal_file_number:
            year = date.today().strftime("%y")
            last_record = FileRecord.objects.select_for_update().order_by('id').last()
            new_id = (last_record.id + 1) if last_record else 1
            self.internal_file_number = f"RL-{year}-{new_id:05d}"
        super().save(*args, **kwargs)


class Comorbidity(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Comorbidities"

    def __str__(self):
        return self.name


class PatientMedicalInfo(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE, help_text="Patient associated with the medical information", verbose_name="Patient")
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, help_text="Blood group of the patient", verbose_name="Blood Group")   
    family_history = models.TextField(help_text="Family medical history of the patient", verbose_name="Family History", blank=True, null=True)
    known_allergies = models.TextField(help_text="Known allergies of the patient", verbose_name="Known Allergies", blank=True, null=True)
    smokes = models.BooleanField(help_text="Whether the patient smokes or not", verbose_name="Smokes")
    alcoholic = models.BooleanField(help_text="Whether the patient is an alcoholic or not", verbose_name="Alcoholic")
    comorbidities = models.ManyToManyField(Comorbidity, help_text="Comorbidities of the patient", verbose_name="Comorbidities", blank=True)

    def __str__(self):
        return f"Medical Information for {self.patient.get_full_name()} | Blood Group: {self.blood_group}"
    



class Doctor(models.Model):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_doctors'
    )


    name = models.CharField(max_length=255, help_text="Name of the doctor", verbose_name="Doctor Name")
    contact_no = models.CharField(max_length=20,validators=[phone_validator], help_text="Contact number of the doctor", verbose_name="Contact Number")
    email = models.EmailField(help_text="Email address of the doctor", verbose_name="Email Address")
    highest_qualification = models.CharField(max_length=255, help_text="Highest qualification of the doctor", verbose_name="Highest Qualification")
    specialization = models.CharField(max_length=255, help_text="Specialization of the doctor", verbose_name="Specialization")
    years_of_experience = models.IntegerField(help_text="Years of experience of the doctor")

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name
    
class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(
        PatientProfile, 
        on_delete=models.CASCADE, 
        related_name='doctor_assignments'
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name='patient_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # Ek patient ko ek doctor se ek hi baar map kiya ja sake
        unique_together = ('patient', 'doctor')
        verbose_name = "Patient-Doctor Mapping"

    def __str__(self):
        return f"{self.patient.get_full_name()} assigned to {self.doctor.name}"