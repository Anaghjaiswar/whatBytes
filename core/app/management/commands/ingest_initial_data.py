from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date
from django.db import transaction

from app.models import (
    PatientProfile,
    Comorbidity,
    PatientMedicalInfo,
    Doctor,
    PatientDoctorMapping,
    FileRecord,
)


class Command(BaseCommand):
    help = "Create initial data for development and testing."

    def handle(self, *args, **options):
        User = get_user_model()

        with transaction.atomic():
            admin, created = User.objects.get_or_create(
                username="HireMeWhatBytes",
                defaults={
                    "email": "hireMe@whatbytes.com",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )

            if created:
                admin.set_password("admin")
                admin.save()

            # Realistic Indian comorbidities
            comorbidity_names = [
                "Diabetes Mellitus",
                "Hypertension",
                "Chronic Kidney Disease",
                "Chronic Obstructive Pulmonary Disease",
                "Hypothyroidism",
            ]
            com_objs = []
            for name in comorbidity_names:
                obj, _ = Comorbidity.objects.get_or_create(name=name)
                com_objs.append(obj)

            # Create 5 genuine Indian patients
            patient_data = [
                {"first": "Aarav", "last": "Sharma", "dob": date(1988, 3, 12), "sex": "M", "phone": "+919812345678", "email": "aarav.sharma@example.com", "type": "Regular"},
                {"first": "Saanvi", "last": "Patel", "dob": date(1992, 7, 5), "sex": "F", "phone": "+919876543210", "email": "saanvi.patel@example.com", "type": "Regular"},
                {"first": "Rohan", "last": "Kumar", "dob": date(1985, 11, 20), "sex": "M", "phone": "+919701234567", "email": "rohan.kumar@example.com", "type": "Free"},
                {"first": "Priya", "last": "Singh", "dob": date(1995, 2, 14), "sex": "F", "phone": "+919900112233", "email": "priya.singh@example.com", "type": "Regular"},
                {"first": "Arjun", "last": "Reddy", "dob": date(1979, 9, 30), "sex": "M", "phone": "+919845667788", "email": "arjun.reddy@example.com", "type": "Free"},
            ]

            patients = []
            for pdata in patient_data:
                p = PatientProfile.objects.create(
                    created_by=admin,
                    first_name=pdata["first"],
                    last_name=pdata["last"],
                    date_of_birth=pdata["dob"],
                    sex=pdata["sex"],
                    contact_no=pdata["phone"],
                    email=pdata["email"],
                    type=pdata["type"],
                )
                patients.append(p)

            # Create medical info for each patient and attach one comorbidity
            blood_groups = ["A+", "B+", "O+", "AB+", "A-"]
            for i, p in enumerate(patients):
                mi = PatientMedicalInfo.objects.create(
                    patient=p,
                    blood_group=blood_groups[i % len(blood_groups)],
                    family_history="No significant family history",
                    known_allergies="None",
                    smokes=(i % 2 == 0),
                    alcoholic=(i % 3 == 0),
                )
                mi.comorbidities.add(com_objs[i % len(com_objs)])

            # Create 5 Indian doctors with realistic details
            doctor_data = [
                {"name": "Dr. Amit Verma", "phone": "+919860000001", "email": "amit.verma@hospital.example", "qualification": "MBBS, MD", "specialization": "Cardiology", "exp": 15},
                {"name": "Dr. Neha Rao", "phone": "+919860000002", "email": "neha.rao@hospital.example", "qualification": "MBBS, DGO", "specialization": "General Medicine", "exp": 10},
                {"name": "Dr. Vikram Iyer", "phone": "+919860000003", "email": "vikram.iyer@hospital.example", "qualification": "MBBS, DNB", "specialization": "Pulmonology", "exp": 12},
                {"name": "Dr. Meera Menon", "phone": "+919860000004", "email": "meera.menon@hospital.example", "qualification": "MBBS, MD", "specialization": "Endocrinology", "exp": 9},
                {"name": "Dr. Suresh Rao", "phone": "+919860000005", "email": "suresh.rao@hospital.example", "qualification": "MBBS, DM", "specialization": "Nephrology", "exp": 20},
            ]

            doctors = []
            for ddata in doctor_data:
                d = Doctor.objects.create(
                    created_by=admin,
                    name=ddata["name"],
                    contact_no=ddata["phone"],
                    email=ddata["email"],
                    highest_qualification=ddata["qualification"],
                    specialization=ddata["specialization"],
                    years_of_experience=ddata["exp"],
                )
                doctors.append(d)

            # Map each patient to a doctor (one-to-one mapping here)
            for i, p in enumerate(patients):
                PatientDoctorMapping.objects.get_or_create(
                    patient=p, doctor=doctors[i], defaults={"is_active": True}
                )

            # Ensure FileRecords exist (signal creates them on patient save, but make double-sure)
            for p in patients:
                FileRecord.objects.get_or_create(patient=p)

        self.stdout.write(self.style.SUCCESS("Initial ingest: created 5 records per model."))
