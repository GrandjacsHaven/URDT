import os
import csv
import random
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from urdt_app.models import (
    Phase, Cohort, Sector, Occupation, District, TraineeApplication
)

# Define paths (Modify this if needed)
CSV_FILE_PATH = r"D:\DJANGO\URDT\static\data\output.csv"

class Command(BaseCommand):
    help = "Populates the database with dummy trainee data from a CSV file."

    def handle(self, *args, **options):
        # Check if the CSV file exists
        if not os.path.exists(CSV_FILE_PATH):
            self.stderr.write(f"❌ Error: File not found at {CSV_FILE_PATH}")
            return

        # Ensure a default phase exists
        default_phase, _ = Phase.objects.get_or_create(name="Default Phase")

        # Store existing or new Cohorts, Sectors, Districts, and Occupations
        cohort_map = {}
        sector_map = {}
        occupation_map = {}
        district_map = {}

        # Read the CSV file
        with open(CSV_FILE_PATH, newline='', encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header row
            
            # Expected column indexes based on sample data
            COL_NAME = 1
            COL_GENDER = 2
            COL_AGE = 3
            COL_TRAINING_COMPLETE = 5
            COL_DIT_ASSESSED = 6
            COL_PASSED_DIT = 7
            COL_SECTOR = 8
            COL_OCCUPATION = 9
            COL_SELF_EMPLOYED = 10
            COL_EMPLOYED = 11
            COL_DISTRICT = 12
            COL_COHORT = 15  # This is where cohort names are stored correctly

            trainees_created = 0

            for row in reader:
                if not row or len(row) < 16:  # Ensure row has expected columns
                    continue

                # Extract values safely
                applicant_name = row[COL_NAME].strip() if row[COL_NAME] else "Unknown"
                gender = row[COL_GENDER].strip() if row[COL_GENDER] else "Unknown"
                age = int(row[COL_AGE].strip()) if row[COL_AGE].isdigit() else random.randint(18, 35)

                training_complete = row[COL_TRAINING_COMPLETE].strip().upper() == "YES"
                dit_assessed = row[COL_DIT_ASSESSED].strip().upper() == "YES"
                passed_dit = row[COL_PASSED_DIT].strip().upper() == "YES"

                sector_name = row[COL_SECTOR].strip().title() if row[COL_SECTOR] else "Unknown"
                occupation_name = row[COL_OCCUPATION].strip().title() if row[COL_OCCUPATION] else "General Worker"

                self_employed = row[COL_SELF_EMPLOYED].strip().upper() == "YES"
                employed = row[COL_EMPLOYED].strip().upper() == "YES"

                district_name = row[COL_DISTRICT].strip().title() if row[COL_DISTRICT] else "Unknown"
                
                # Ensure cohort name is properly formatted
                raw_cohort_name = row[COL_COHORT].strip().upper() if row[COL_COHORT] else "COHORT UNKNOWN"
                cohort_name = raw_cohort_name.replace("  ", " ").replace("COHORT", "COHORT").strip()

                # Fix cohort naming issue
                if not cohort_name.startswith("COHORT"):
                    cohort_name = f"COHORT {cohort_name}"  # Ensure correct format

                # Create or get Cohort
                if cohort_name not in cohort_map:
                    cohort_obj, _ = Cohort.objects.get_or_create(name=cohort_name, phase=default_phase)
                    cohort_map[cohort_name] = cohort_obj
                cohort = cohort_map[cohort_name]

                # Create or get Sector
                if sector_name not in sector_map:
                    sector_obj, _ = Sector.objects.get_or_create(name=sector_name)
                    sector_map[sector_name] = sector_obj
                sector = sector_map[sector_name]

                # Create or get Occupation
                occupation_key = f"{sector_name}-{occupation_name}"  # Unique key for each sector-occupation pair
                if occupation_key not in occupation_map:
                    occupation_obj, _ = Occupation.objects.get_or_create(name=occupation_name, sector=sector)
                    occupation_map[occupation_key] = occupation_obj
                occupation = occupation_map[occupation_key]

                # Create or get District
                if district_name not in district_map:
                    district_obj, _ = District.objects.get_or_create(name=district_name)
                    district_map[district_name] = district_obj
                district = district_map[district_name]

                # Determine study status
                study_status = "COMPLETED" if training_complete else "STARTED_STUDYING"
                final_assessment_status = "SUCCESSFUL" if passed_dit else "NONE"

                # Randomized nationality & disability
                nationality = random.choice(["Ugandan", "Refugee"])
                pwd = random.choice([True, False])

                # Create trainee
                trainee = TraineeApplication.objects.create(
                    cohort=cohort,
                    training_year_month=f"{now().year}-{now().month}",
                    applicant_name=applicant_name,
                    phone_contact="07" + str(random.randint(10000000, 99999999)),  # Generate fake phone number
                    phone_ownership=random.choice(["Personal", "Family", "Community"]),
                    gender=gender,
                    date_of_birth=now().date().replace(year=now().year - age),  # Approximate DOB
                    age=age,
                    consent_form_obtained=random.choice([True, False]),
                    marital_status=random.choice(["Single", "Married", "Divorced", "Widowed"]),
                    district=district,
                    nationality=nationality,
                    pwd=pwd,
                    nature_of_disability="None" if not pwd else "Visual Impairment",
                    education_level=random.choice(["Primary", "Secondary", "Tertiary", "University", "Not at all"]),
                    religion=random.choice(["Christian", "Muslim", "Other"]),
                    employment_status="Self-employed" if self_employed else ("Employed" if employed else "Unemployed"),
                    monthly_income=random.choice(["Below 100,000", "100,000 - 299,000", "300,000 - 500,000", "Above 500,000"]),
                    sector=sector,
                    occupation=occupation,
                    has_smartphone=random.choice([True, False]),
                    internet_access=random.choice([True, False]),
                    online_platform_awareness=random.choice([True, False]),
                    family_role=random.choice(["Father", "Mother", "Guardian", "Child", "Other"]),
                    healthcare_access=random.choice(["Use traditional herbs", "Go to hospital", "Clinic", "Other"]),
                    community_leader=random.choice([True, False]),
                    has_vision=random.choice([True, False]),
                    vision_description="I want to start a business" if random.choice([True, False]) else None,
                    mentees="John, Mary, Peter, Susan, Robert",
                    study_status=study_status,
                    dit_status="REGISTERED" if dit_assessed else "NOT_REGISTERED",
                    final_assessment_status=final_assessment_status,
                    created_at=now()
                )

                trainees_created += 1

            self.stdout.write(f"✅ Successfully created {trainees_created} trainees!")
