import csv
import random

OUTPUT_CSV = "trainees_test.csv"
NUM_RECORDS = 60000

# Lists for generating random names
first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Irene', 'Jack']
last_names = ['Doe', 'Smith', 'Brown', 'Johnson', 'Williams', 'Jones', 'Davis', 'Miller', 'Wilson', 'Moore']

# Gender options
genders = ['Male', 'Female']

# Weighted choices for PWD (20% yes) and Refugee (10% yes)
pwd_choices = ['yes', 'no']
refugee_choices = ['yes', 'no']

# Training-related fields (random yes/no)
training_choices = ['yes', 'no']
entrepreneur_choices = ['yes', 'no']
employed_choices = ['yes', 'no']

# Sectors and corresponding occupations
sectors = {
    "Agriculture": ["Farmer", "Agronomist", "Crop Specialist", "Veterinarian"],
    "Tourism": ["Tour Guide", "Hotel Manager", "Travel Consultant", "Chef"],
    "Construction": ["Builder", "Carpenter", "Architect", "Engineer"]
}
sector_list = list(sectors.keys())

# Simulate many districts and other location details
districts = ["Kampala", "Wakiso", "Jinja", "Gulu", "Mbarara", "Mbale", "Lira", "Masaka", "Mityana", "Entebbe"]
villages = ["Village A", "Village B", "Village C", "Village D", "Village E", "Village F", "Village G", "Village H"]
parishes = ["Parish 1", "Parish 2", "Parish 3", "Parish 4", "Parish 5", "Parish 6"]
sub_counties = ["SubCounty X", "SubCounty Y", "SubCounty Z", "SubCounty W", "SubCounty V"]

# Fixed phase (all under Phase 1) and multiple cohorts (1-9)
phase = "Phase 1"
cohorts = [f"Cohort {i}" for i in range(1, 10)]  # Cohort 1 to Cohort 9

# CSV header as expected by the import utility
headers = [
    "Name", "Gender", "Age", "Contact", "PWD", "Refugee", "Completed Training",
    "DIT Assessed", "Passed DIT", "Sector", "Occupation", "Entrepreneurs",
    "Employed", "District", "Village", "Parish", "Sub County", "Phase", "Cohort"
]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()

    for i in range(NUM_RECORDS):
        # Generate a random full name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"

        # Random gender and age
        gender = random.choice(genders)
        age = str(random.randint(18, 60))
        # Ensure each contact is unique
        contact = f"{1000000000 + i}"

        # Weighted random selections:
        pwd = random.choices(pwd_choices, weights=[0.2, 0.8], k=1)[0]
        refugee = random.choices(refugee_choices, weights=[0.1, 0.9], k=1)[0]

        # Random training fields
        completed_training = random.choice(training_choices)
        dit_assessed = random.choice(training_choices)
        passed_dit = random.choice(training_choices)

        # Randomly choose a sector and then an occupation under that sector
        sector = random.choice(sector_list)
        occupation = random.choice(sectors[sector])

        # Random values for entrepreneurs and employment
        entrepreneurs = random.choice(entrepreneur_choices)
        employed = random.choice(employed_choices)

        # Random location details
        district = random.choice(districts)
        village = random.choice(villages)
        parish = random.choice(parishes)
        sub_county = random.choice(sub_counties)

        # Randomly assign a cohort from 1 to 9
        cohort = random.choice(cohorts)

        record = {
            "Name": name,
            "Gender": gender,
            "Age": age,
            "Contact": contact,
            "PWD": pwd,
            "Refugee": refugee,
            "Completed Training": completed_training,
            "DIT Assessed": dit_assessed,
            "Passed DIT": passed_dit,
            "Sector": sector,
            "Occupation": occupation,
            "Entrepreneurs": entrepreneurs,
            "Employed": employed,
            "District": district,
            "Village": village,
            "Parish": parish,
            "Sub County": sub_county,
            "Phase": phase,
            "Cohort": cohort
        }
        writer.writerow(record)

print(f"CSV file '{OUTPUT_CSV}' with {NUM_RECORDS} records has been created.")














#DELETE ALL TRAINEE RECORDS FROM DB


# from urdt_app.models import TraineeApplication

# # Delete all trainee records
# TraineeApplication.objects.all().delete()

# print("All trainee records have been deleted.")