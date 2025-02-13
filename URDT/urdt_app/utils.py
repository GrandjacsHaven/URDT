# utils.py
import csv
import random
from io import TextIOWrapper
from datetime import date
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
from .models import TraineeApplication, Sector, Occupation, District, Phase, Cohort, ImportProgress

BATCH_SIZE = 1000  # Process in batches of 1,000

def import_trainees_from_csv(file_obj, progress):
    """
    Import trainees from a CSV file–like object while updating the progress model.
    Also creates a CustomUser for each trainee and assigns student numbers in bulk.
    
    Returns a tuple: (imported_count, skipped_count)
    """
    imported_count = 0
    skipped_count = 0

    # Wrap the file object (assumed to be binary) with a text wrapper and load all rows.
    text_file = TextIOWrapper(file_obj, encoding='utf-8')
    reader = csv.DictReader(text_file)
    rows = list(reader)
    total_rows = len(rows)
    progress.total_records = total_rows
    progress.save()

    # --- Duplicate Prevention Optimization ---
    existing_keys = set()
    for values in TraineeApplication.objects.all().values_list(
            'applicant_name', 'gender', 'phone_contact', 'study_status', 'dit_status',
            'final_assessment_status', 'employment_status', 'sector__name', 'occupation__name',
            'district__name', 'village', 'parish', 'subcounty', 'cohort__name'):
        key = tuple((v or '').strip().lower() for v in values)
        existing_keys.add(key)

    # --- In-Memory Caching for Related Objects ---
    sector_cache = {s.name.lower(): s for s in Sector.objects.all()}
    occupation_cache = {(o.sector.name.lower() if o.sector and o.sector.name else '') + '_' + o.name.lower(): o
                        for o in Occupation.objects.all()}
    district_cache = {d.name.lower(): d for d in District.objects.all()}
    phase_cache = {p.name.lower(): p for p in Phase.objects.all()}
    cohort_cache = {(c.phase.name.lower() if c.phase and c.phase.name else '') + '_' + c.name.lower(): c
                    for c in Cohort.objects.all()}
    default_phase, _ = Phase.objects.get_or_create(name="DEFAULT PHASE")
    phase_cache["default phase"] = default_phase

    # --- Preload Existing Usernames ---
    existing_usernames = set(CustomUser.objects.values_list('username', flat=True))

    # Batches to accumulate objects before bulk insertion.
    trainee_batch = []  # List of TraineeApplication instances (unsaved)
    user_batch = []     # List of CustomUser instances (unsaved)
    new_keys = set()    # Keys for trainees imported during this run
    batch_usernames = set()  # Track usernames in the current batch

    for i, row in enumerate(rows):
        # Normalize and strip CSV values
        name = row.get('Name', '').strip()
        gender = row.get('Gender', '').strip().title()  # Ensure "Male" or "Female"
        age_str = row.get('Age', '').strip()
        contact = row.get('Contact', '').strip()
        pwd_val = row.get('PWD', '').strip().lower()
        refugee_val = row.get('Refugee', '').strip().lower()
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
            # Update progress after processing this row.
            progress.processed_records = i + 1
            progress.imported_count = imported_count
            progress.skipped_count = skipped_count
            progress.save()
            continue

        try:
            age_val = int(age_str)
        except ValueError:
            age_val = 0

        # Compute default date_of_birth based on age (assume January 1st)
        current_year = date.today().year
        birth_year = current_year - age_val if age_val > 0 else current_year - 25
        dob = date(birth_year, 1, 1)

        # Map CSV values to model statuses
        study_status = "COMPLETED" if completed_training == "yes" else "NOT_STARTED"
        dit_status = "REGISTERED" if dit_assessed == "yes" else "NOT_REGISTERED"
        final_assessment_status = "SUCCESSFUL" if passed_dit_val == "yes" else "UNSUCCESSFUL"
        if entrepreneurs_val == "yes":
            employment_status = "Self-employed"
        elif employed_val == "yes":
            employment_status = "Employed"
        else:
            employment_status = "Unemployed"

        pwd_value = True if pwd_val == "yes" else False
        nationality_value = "Refugee" if refugee_val == "yes" else "Ugandan"

        # --- Fetch Related Objects from Cache (or create if missing) ---
        sector_obj = None
        if sector_name:
            key_sector = sector_name.lower()
            sector_obj = sector_cache.get(key_sector)
            if not sector_obj:
                sector_obj = Sector.objects.create(name=sector_name)
                sector_cache[key_sector] = sector_obj

        occupation_obj = None
        if occupation_name and sector_obj:
            key_occupation = f"{sector_obj.name.lower()}_{occupation_name.lower()}"
            occupation_obj = occupation_cache.get(key_occupation)
            if not occupation_obj:
                occupation_obj = Occupation.objects.create(sector=sector_obj, name=occupation_name)
                occupation_cache[key_occupation] = occupation_obj

        district_obj = None
        if district_name:
            key_district = district_name.lower()
            district_obj = district_cache.get(key_district)
            if not district_obj:
                district_obj = District.objects.create(name=district_name)
                district_cache[key_district] = district_obj

        phase_obj = None
        if phase_name:
            key_phase = phase_name.lower()
            phase_obj = phase_cache.get(key_phase)
            if not phase_obj:
                phase_obj = Phase.objects.create(name=phase_name)
                phase_cache[key_phase] = phase_obj

        cohort_obj = None
        if cohort_name and phase_obj:
            key_cohort = f"{phase_obj.name.lower()}_{cohort_name.lower()}"
            cohort_obj = cohort_cache.get(key_cohort)
            if not cohort_obj:
                cohort_obj = Cohort.objects.create(name=cohort_name, phase=phase_obj)
                cohort_cache[key_cohort] = cohort_obj

        # --- Duplicate Prevention: Build a normalized key tuple ---
        key_tuple = (
            name.lower(), gender.lower(), contact.lower(), 
            study_status.lower(), dit_status.lower(), final_assessment_status.lower(),
            employment_status.lower(),
            (sector_obj.name.lower() if sector_obj else ''),
            (occupation_obj.name.lower() if occupation_obj else ''),
            (district_obj.name.lower() if district_obj else ''),
            village.lower(), parish.lower(), subcounty.lower(),
            (cohort_obj.name.lower() if cohort_obj else '')
        )
        if key_tuple in existing_keys or key_tuple in new_keys:
            skipped_count += 1
            progress.processed_records = i + 1
            progress.imported_count = imported_count
            progress.skipped_count = skipped_count
            progress.save()
            continue
        new_keys.add(key_tuple)

        # --- Create a CustomUser for the trainee ---
        base_username = ''.join(name.lower().split())
        username = base_username
        suffix = 1
        while username in existing_usernames or username in batch_usernames:
            username = f"{base_username}{suffix}"
            suffix += 1
        batch_usernames.add(username)
        existing_usernames.add(username)

        default_email = f"{username}@example.com"
        default_password = "password123"

        user = CustomUser(
            username=username,
            email=default_email,
            role='TRAINEE',
            designation='General'
        )
        user.set_password(default_password)
        user_batch.append(user)

        # --- Create TraineeApplication object; temporarily store username for linking ---
        trainee = TraineeApplication(
            cohort=cohort_obj,
            applicant_name=name,
            phone_contact=contact,
            gender=gender,
            age=age_val,
            date_of_birth=dob,
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
            pwd=pwd_value,
            nationality=nationality_value,
            training_year_month="",
            phone_ownership="",
            marital_status="Single",
            consent_form_obtained=False,
            current_location="",
            zone="",
            block_number="",
            nature_of_disability="",
            education_level="Not at all",
            religion="Christian",
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
        trainee._temp_username = username
        trainee_batch.append(trainee)

        # Process a batch if we reach the defined batch size.
        if len(trainee_batch) >= BATCH_SIZE:
            CustomUser.objects.bulk_create(user_batch)
            created_users = CustomUser.objects.filter(username__in=[u.username for u in user_batch])
            user_dict = {u.username: u for u in created_users}
            for t in trainee_batch:
                t.created_by = user_dict.get(t._temp_username)
                del t._temp_username
            TraineeApplication.objects.bulk_create(trainee_batch)
            imported_count += len(trainee_batch)
            trainee_batch.clear()
            user_batch.clear()
            batch_usernames.clear()

        # Update progress after processing each row.
        progress.processed_records = i + 1
        progress.imported_count = imported_count
        progress.skipped_count = skipped_count
        progress.save()

    # Process any remaining records in the batches.
    if trainee_batch:
        CustomUser.objects.bulk_create(user_batch)
        created_users = CustomUser.objects.filter(username__in=[u.username for u in user_batch])
        user_dict = {u.username: u for u in created_users}
        for t in trainee_batch:
            t.created_by = user_dict.get(t._temp_username)
            del t._temp_username
        TraineeApplication.objects.bulk_create(trainee_batch)
        imported_count += len(trainee_batch)
        trainee_batch.clear()
        user_batch.clear()
        batch_usernames.clear()

    # --- Bulk Update: Generate and assign student numbers ---
    trainees_without_number = list(TraineeApplication.objects.filter(student_number__isnull=True))
    existing_student_numbers = set(TraineeApplication.objects.exclude(student_number__isnull=True)
                                    .values_list('student_number', flat=True))
    updated_trainees = []
    for trainee in trainees_without_number:
        while True:
            candidate = str(random.randint(1000, 9999))
            if candidate not in existing_student_numbers:
                existing_student_numbers.add(candidate)
                trainee.student_number = candidate
                break
        updated_trainees.append(trainee)
    if updated_trainees:
        TraineeApplication.objects.bulk_update(updated_trainees, ['student_number'])

    # Final update of progress.
    progress.processed_records = total_rows
    progress.imported_count = imported_count
    progress.skipped_count = skipped_count
    progress.completed = True
    progress.save()

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


