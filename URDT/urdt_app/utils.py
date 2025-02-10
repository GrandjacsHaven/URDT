import csv
from io import TextIOWrapper
from datetime import date
from django.db import transaction
from .models import (
    TraineeApplication, Sector, Occupation, District, Phase, Cohort
)

@transaction.atomic
def import_trainees_from_csv(file_obj):
    """
    Import trainees from a CSV file–like object.
    
    The CSV is expected to have these columns (exact header names):
      Name, Gender, Age, Contact, Completed Training, DIT Assessed, Passed DIT,
      Sector, Occupation, Entrepreneurs, Employed, District, Village, Parish,
      Sub County, Phase, Cohort

    Mapping & logic (all comparisons are case‑insensitive):
      - Name, Gender, Age, Contact are imported directly.
      - Completed Training: "yes" → study_status = COMPLETED; otherwise NOT_STARTED.
      - DIT Assessed: "yes" → dit_status = REGISTERED; otherwise NOT_REGISTERED.
      - Passed DIT: "yes" → final_assessment_status = SUCCESSFUL; any other value (or blank) → UNSUCCESSFUL.
      - For employment, if Entrepreneurs is "yes", then set employment_status = Self-employed;
        else if Employed is "yes", then Employed; otherwise Unemployed.
      - For Sector, Occupation, District, Phase, and Cohort: do a case‑insensitive lookup; if not found, create new.
      - Duplicate prevention: if a TraineeApplication exists whose key fields (name, gender, contact,
        study_status, dit_status, final_assessment_status, employment_status, and the related FK objects,
        plus village, parish, subcounty) match (using case‑insensitive comparison where applicable),
        then skip the row.
    
    Returns a tuple: (imported_count, skipped_count)
    """
    imported_count = 0
    skipped_count = 0

    # Wrap the file object (assumed to be binary) with a text wrapper.
    text_file = TextIOWrapper(file_obj, encoding='utf-8')
    reader = csv.DictReader(text_file)

    for row in reader:
        # Normalize and strip values
        name = row.get('Name', '').strip()
        gender = row.get('Gender', '').strip().title()  # Ensure "Male" or "Female"
        age_str = row.get('Age', '').strip()
        contact = row.get('Contact', '').strip()
        completed_training = row.get('Completed Training', '').strip().lower()
        dit_assessed = row.get('DIT Assessed', '').strip().lower()
        passed_dit_val = row.get('Passed DIT', '').strip().lower()
        sector_name = row.get('Sector', '').strip()
        occupation_name = row.get('Occupation', '').strip()
        entrepreneurs_val = row.get('Entrepreneurs', '').strip().lower()
        employed_val = row.get('Employed', '').strip().lower()
        district_name = row.get('District', '').strip()
        village = row.get('Village', '').strip()
        parish = row.get('Parish', '').strip()
        subcounty = row.get('Sub County', '').strip()
        phase_name = row.get('Phase', '').strip()
        cohort_name = row.get('Cohort', '').strip()

        # Skip if mandatory fields are missing
        if not name or not contact:
            skipped_count += 1
            continue

        try:
            age_val = int(age_str)
        except ValueError:
            age_val = 0

        # Compute a default date_of_birth based on the age:
        # Assume the trainee was born on January 1st of (current year - age).
        current_year = date.today().year
        birth_year = current_year - age_val if age_val > 0 else current_year - 25
        dob = date(birth_year, 1, 1)

        # Map CSV values to model fields
        study_status = "COMPLETED" if completed_training == "yes" else "NOT_STARTED"
        dit_status = "REGISTERED" if dit_assessed == "yes" else "NOT_REGISTERED"
        final_assessment_status = "SUCCESSFUL" if passed_dit_val == "yes" else "UNSUCCESSFUL"
        if entrepreneurs_val == "yes":
            employment_status = "Self-employed"
        elif employed_val == "yes":
            employment_status = "Employed"
        else:
            employment_status = "Unemployed"

        # Get or create related objects using case‑insensitive lookups
        if sector_name:
            sector_obj, _ = Sector.objects.get_or_create(name__iexact=sector_name, defaults={'name': sector_name})
        else:
            sector_obj = None

        if occupation_name and sector_obj:
            occupation_obj, _ = Occupation.objects.get_or_create(
                sector=sector_obj,
                name__iexact=occupation_name,
                defaults={'name': occupation_name}
            )
        else:
            occupation_obj = None

        if district_name:
            district_obj, _ = District.objects.get_or_create(name__iexact=district_name, defaults={'name': district_name})
        else:
            district_obj = None

        if phase_name:
            phase_obj, _ = Phase.objects.get_or_create(name__iexact=phase_name, defaults={'name': phase_name})
        else:
            phase_obj = None

        if cohort_name and phase_obj:
            cohort_obj, _ = Cohort.objects.get_or_create(
                phase=phase_obj,
                name__iexact=cohort_name,
                defaults={'name': cohort_name}
            )
        else:
            cohort_obj = None

        # Check for duplicates using key fields (all case‑insensitive where applicable)
        duplicate = TraineeApplication.objects.filter(
            applicant_name__iexact=name,
            gender__iexact=gender,
            phone_contact__iexact=contact,
            study_status=study_status,
            dit_status=dit_status,
            final_assessment_status=final_assessment_status,
            employment_status__iexact=employment_status,
            sector=sector_obj,
            occupation=occupation_obj,
            district=district_obj,
            village__iexact=village,
            parish__iexact=parish,
            subcounty__iexact=subcounty,
            cohort=cohort_obj,
        ).exists()

        if duplicate:
            skipped_count += 1
            continue

        # Create a new TraineeApplication record.
        trainee = TraineeApplication(
            cohort=cohort_obj,
            applicant_name=name,
            phone_contact=contact,
            gender=gender,
            age=age_val,
            date_of_birth=dob,  # Now supplying a default based on age.
            study_status=study_status,
            dit_status=dit_status,
            final_assessment_status=final_assessment_status,
            employment_status=employment_status,
            sector=sector_obj,
            occupation=occupation_obj,
            district=district_obj,
            village=village,
            parish=parish,
            subcounty=subcounty,
            # The following fields are not provided by the CSV; set defaults or leave blank.
            training_year_month="",
            phone_ownership="",
            marital_status="Single",  # Default value; adjust as needed.
            consent_form_obtained=False,
            current_location="",
            zone="",
            block_number="",
            nationality="Ugandan",  # Default value.
            pwd=False,
            nature_of_disability="",
            education_level="Not at all",
            religion="Christian",  # Default value.
            other_assets="",
            household_members_above_15=0,
            meals_per_day="Once",
            internet_access=False,
            online_platform_awareness=False,
            family_role="Child",
            healthcare_access="Go to hospital",
            community_leader=False,
            has_vision=False,
            vision_description="",
            mentees="",
        )
        trainee.save()  # This will auto‑generate the student_number.
        imported_count += 1

    return imported_count, skipped_count


def superuser_required(user):
    return user.is_authenticated and user.role == "SUPER_USER"

def administrative_user_required(user):
    return user.is_authenticated and user.role == "ADMINISTRATIVE_USER"

def sub_admin_required(user):
    return user.is_authenticated and user.role == "SUB_ADMIN"

def epicenter_manager_required(user):
    return user.is_authenticated and user.role == "EPICENTER_MANAGER"

def trainee_required(user):
    return user.is_authenticated and user.role == "TRAINEE"

def sector_lead_required(user):
    return user.is_authenticated and user.role == "SECTOR_LEAD" and user.sector is not None

def trainer_required(user):
    return user.is_authenticated and user.role == "TRAINER"

def data_entrant_required(user):
    return user.is_authenticated and user.role == "DATA_ENTRANT"

def safeguarding_officer_required(user):
    return user.is_authenticated and user.designation == 'Safe Guarding Officer'

def stakeholder_required(user):
    if not user.is_authenticated:
        return False
    
    designations = [
        'M&E Officer', 'Principal', 'Accountant', 'Project Manager'
    ]
    if user.role == 'SECTOR_LEAD':
        return True
    if user.designation in designations:
        return True
    return False


