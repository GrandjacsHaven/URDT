from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
import uuid  # For possible unique IDs
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import random

# Custom User Model
class CustomUser(AbstractUser):
    """
    Custom user model with roles, designations, and additional permissions.
    """
    ROLE_CHOICES = [
        ('SUPER_USER', 'Super User'),
        ('ADMINISTRATIVE_USER', 'Admin'),
        ('SUB_ADMIN', 'Sub Admin'),
        ('EPICENTER_MANAGER', 'Epicenter Manager'),
        ('SECTOR_LEAD', 'Sector Lead'),
        ('DATA_ENTRANT', 'Data Entrant'),
        ('TRAINER', 'Trainer'),
        ('TRAINEE', 'Trainee'),
    ]

    DESIGNATION_CHOICES = [
        # SUB_ADMIN Designations
        ('Project Manager', 'Project Manager'),
        ('CEO', 'CEO'),
        ('Academic Registrar', 'Academic Registrar'),
        ('Director Education and Training', 'Director Education and Training'),
        ('Director Finance and Admin', 'Director Finance and Admin'),
        ('Director Epicentre Strategy', 'Director Epicentre Strategy'),
        ('Director Cooperate Relations', 'Director Corporate Relations'),
        ('Human Resource', 'Human Resource'),
        ('Safe Guarding Officer', 'Safeguarding Officer'),
        ('Principal', 'Principal'),
        ('Accountant', 'Accountant'),

        # ADMINISTRATIVE_USER Designations
        ('M&E Officer', 'M&E Officer'),
        ('MERL Coordinator', 'MERL Coordinator'),
        ('IT Officer', 'IT Officer'),

        #TRAINER Designations
        ('Artisan', 'Artisan'),
        ('Agribusiness Practitioner', 'Agribusiness Practitioner'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SECTOR_LEAD')
    designation = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    sector = models.ForeignKey(
        'Sector', on_delete=models.SET_NULL, null=True, blank=True, related_name='sector_leads'
    )
    district = models.ForeignKey(
        'District', on_delete=models.SET_NULL, null=True, blank=True, related_name='epicenter_managers'
    )
    data_entrant_district = models.ForeignKey(
        'District', on_delete=models.SET_NULL, null=True, blank=True, related_name='data_entrants'
    )
    can_enroll_trainees = models.BooleanField(default=False, help_text="Can enroll trainees")
    can_enroll_trainers = models.BooleanField(default=False, help_text="Can enroll trainers")
    can_edit_trainees = models.BooleanField(default=False, help_text="Can edit assigned trainees")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"



    




















          #*Super User related models*#




# Phase Model
class Phase(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




# Cohort Model
class Cohort(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='cohorts')
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phase.name})"

#sector model
class Sector(models.Model):
    name = models.CharField(max_length=100)
    
    # Updated: Trainer designations specific to the sector
    TRAINER_DESIGNATIONS = [
        ('Artisan', 'Artisan'),
        ('Agribusiness Practitioner', 'Agribusiness Practitioner'),
    ]
    trainer_designation = models.CharField(
        max_length=50,
        choices=TRAINER_DESIGNATIONS,
        blank=True,
        null=True,
        help_text="Only trainers with this designation can be assigned to this sector."
    )

    def __str__(self):
        return self.name


# Occupation Model
class Occupation(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='occupations')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.sector.name})"



# District Model
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Audit Log Model
class AuditLog(models.Model):
    """
    Tracks user activities such as logins, data changes, deletions.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"AuditLog ({self.action}) by {self.user} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    

























# Document Model
class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    designation = models.CharField(max_length=255)  
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name





    

















      #*Epicenter Manager related models*#



    








    






































#Approved Document Model
class ApprovedDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="approved_documents/")
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    











































    
















# ----------------------------------------
# 7) Library Category & Document
# ----------------------------------------
class LibraryCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LibraryDocument(models.Model):
    category = models.ForeignKey(LibraryCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="library_docs/")
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    




























































































class TrainerApplication(models.Model):
    """
    Tracks trainer information and links trainers to specific categories.
    """
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE, 
    related_name='trainerapplication',
    null=True, 
    blank=True
)
    passport_photo = models.ImageField(upload_to="trainer_photos/", null=True, blank=True)
    name = models.CharField(max_length=255)
    phone_contact = models.CharField(max_length=15)
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female')]
    )
    date_of_birth = models.DateField()
    age = models.IntegerField(null=True, blank=True)  # Auto-calculated age
    marital_status = models.CharField(
        max_length=20, 
        choices=[
            ('Single', 'Single'), 
            ('Divorced', 'Divorced'), 
            ('Married', 'Married'), 
            ('Widowed', 'Widowed')
        ]
    )
    has_smartphone = models.BooleanField(choices=[(True, 'Yes'), (False, 'No')])

    business_name = models.CharField(max_length=255, null=True, blank=True)
    legal_status = models.CharField(
        max_length=20, 
        choices=[('Licensed', 'Licensed'), ('Not Licensed', 'Not Licensed')], 
        null=True, blank=True
    )
    account_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    location = models.CharField(max_length=255, null=True, blank=True)
    household_number = models.CharField(max_length=50, null=True, blank=True)
    current_location = models.CharField(max_length=255, null=True, blank=True)
    zone = models.CharField(max_length=50, null=True, blank=True)
    block_number = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(
        max_length=50, 
        choices=[('Ugandan', 'Ugandan'), ('Refugee', 'Refugee')]
    )
    pwd = models.BooleanField(choices=[(True, 'Yes'), (False, 'No')])
    nature_of_disability = models.CharField(max_length=255, null=True, blank=True)

    education_level = models.CharField(
        max_length=50, 
        choices=[
            ('University', 'University'), 
            ('Tertiary', 'Tertiary'), 
            ('Secondary', 'Secondary'), 
            ('Primary', 'Primary'), 
            ('Not at all', 'Not at all')
        ]
    )
    religion = models.CharField(
        max_length=50, 
        choices=[('Christian', 'Christian'), ('Muslim', 'Muslim'), ('Other', 'Other')], 
        null=True, blank=True
    )
    other_religion = models.CharField(max_length=255, null=True, blank=True)

    village = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    subcounty = models.CharField(max_length=255, null=True, blank=True)

    # Relationships
    district = models.ForeignKey(
        'District', on_delete=models.SET_NULL, null=True, blank=True, related_name='trainers'
    )
    sector = models.ForeignKey(
        'Sector', on_delete=models.SET_NULL, null=True, blank=True, related_name='trainers'
    )
    occupation = models.ForeignKey(
        'Occupation', on_delete=models.SET_NULL, null=True, blank=True, related_name='trainer_occupations'
    )

    # Supporting Documents
    bank_statement = models.FileField(upload_to="attachments/bank_statements/", null=True, blank=True)
    business_licence = models.FileField(upload_to="attachments/business_licences/", null=True, blank=True)
    national_id = models.FileField(upload_to="attachments/national_ids/", null=True, blank=True)
    recommendation_letter = models.FileField(upload_to="attachments/recommendation_letters/", null=True, blank=True)
    academic_documents = models.FileField(upload_to="attachments/academic_documents/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Automatically calculate and save age based on the date of birth.
        """
        if self.date_of_birth:
            today = timezone.now().date()
            self.age = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                self.age -= 1
        super().save(*args, **kwargs)



























































































class TraineeApplication(models.Model):
    """Stores all fields in the EXACT order and type requested."""
    cohort = models.ForeignKey(
        'Cohort', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="trainees",
        help_text="Select the cohort for this trainee"
    )

    # 0) Student Number (Auto Generated)
    student_number = models.CharField(
        max_length=4,
        unique=True,
        editable=False,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.applicant_name

    # 1) Passport Photo (Upload)
    passport_photo = models.ImageField(upload_to="trainee_photos/", null=True, blank=True)

    # 2) We'll link to a future user but we store the data in the form
    # (The actual user is created in the view)

    # 8) Year and Month of Training (Text)
    training_year_month = models.CharField(max_length=100)

    # 9) Name of Applicant (Text)
    applicant_name = models.CharField(max_length=255)

    # 10) Phone Contact (Text)
    phone_contact = models.CharField(max_length=15)

    # 11) Phone Ownership (Text)
    phone_ownership = models.CharField(max_length=50)

    # 12) Gender (Text — not limited to choices, as requested)
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female')]
    )

    # 13) Date of Birth (Date picker)
    date_of_birth = models.DateField()

    # 14) Age (auto-calculated)
    age = models.PositiveIntegerField(default=0)

    # 15) Consent Form Obtained (Yes/No => Boolean)
    consent_form_obtained = models.BooleanField(default=False)

    # 16) Marital Status (Single/Divorced/Married/Widowed)
    MARITAL_CHOICES = [
        ('Single', 'Single'),
        ('Divorced', 'Divorced'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
    ]
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES)

    # 17) Household Number (Text)
    household_number = models.CharField(max_length=50, blank=True, null=True)

    current_location = models.CharField(max_length=255, null=True, blank=True)

    # 18) Zone (Text)
    zone = models.CharField(max_length=100, blank=True, null=True)

    # 19) Block Number (Text)
    block_number = models.CharField(max_length=50, blank=True, null=True)

    # 20) Village (Text)
    village = models.CharField(max_length=255, blank=True, null=True)

    # 21) Parish (Text)
    parish = models.CharField(max_length=255, blank=True, null=True)

    # 22) Sub County (Text)
    subcounty = models.CharField(max_length=255, blank=True, null=True)

    # 23) District (Dropdown)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True)

    # 24) Nationality (Ugandan/Refugee)
    NATIONALITY_CHOICES = [
        ('Ugandan', 'Ugandan'),
        ('Refugee', 'Refugee'),
    ]
    nationality = models.CharField(max_length=20, choices=NATIONALITY_CHOICES)

    # 25) PWD (Yes/No => Boolean)
    pwd = models.BooleanField(default=False)

    # NEW: Current location field (requested for epicenter manager updates)
    current_location = models.CharField(max_length=255, blank=True, null=True)

    # 26) Nature of Disability - **now just a text field** (no more dropdown choices)
    nature_of_disability = models.CharField(max_length=255, blank=True, null=True)

    # 27) Education Level (University/Tertiary/Secondary/Primary/Not at all)
    EDUCATION_CHOICES = [
        ('University', 'University'),
        ('Tertiary', 'Tertiary'),
        ('Secondary', 'Secondary'),
        ('Primary', 'Primary'),
        ('Not at all', 'Not at all'),
    ]
    education_level = models.CharField(max_length=50, choices=EDUCATION_CHOICES)

    # 28) Religion (Christian/Moslem/Other)
    RELIGION_CHOICES = [
        ('Christian', 'Christian'),
        ('Moslem', 'Moslem'),
        ('Other', 'Other'),
    ]
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES)

    # 29) Employment Status (Self-employed/Employed/Unemployed)
    EMPLOYMENT_CHOICES = [
        ('Self-employed', 'Self-employed'),
        ('Employed', 'Employed'),
        ('Unemployed', 'Unemployed'),
    ]
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)

    # 30) Current Monthly Income (Below 100,000 / 100,000 - 299,000 / 300,000 - 500,000 / Above 500,000)
    INCOME_CHOICES = [
        ('Below 100,000', 'Below 100,000'),
        ('100,000 - 299,000', '100,000 - 299,000'),
        ('300,000 - 500,000', '300,000 - 500,000'),
        ('Above 500,000', 'Above 500,000'),
    ]
    monthly_income = models.CharField(max_length=30, choices=INCOME_CHOICES)

    # 31) Sector (Dropdown)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE, related_name='trainee_sector')

    # 32) Occupation (Dropdown under the selected sector)
    occupation = models.ForeignKey('Occupation', on_delete=models.CASCADE, related_name='trainee_occupation')

    # 33) Do you have a smartphone? (Yes/No => Boolean)
    has_smartphone = models.BooleanField(default=False)

    # 34) Which other assets do you currently own? (Multiple Select => stored as text or CSV)
    other_assets = models.TextField(blank=True, null=True)

    # 35) Number of young people (15 and above) in your household (Number)
    household_members_above_15 = models.PositiveIntegerField(default=0)

    # 36) How many times does your household have meals per day? (Once, Twice, Thrice)
    MEALS_CHOICES = [
        ('Once', 'Once'),
        ('Twice', 'Twice'),
        ('Thrice', 'Thrice'),
    ]
    meals_per_day = models.CharField(max_length=10, choices=MEALS_CHOICES)

    # 37) Are you able to use a computer or phone to access the internet? (Yes/No => Boolean)
    internet_access = models.BooleanField(default=False)

    # 38) Are you aware of online platforms linking people to meaningful work/market? (Yes/No => Boolean)
    online_platform_awareness = models.BooleanField(default=False)

    # 39) What role do you play in your family? (Father/Mother/Guardian/Child/Other)
    FAMILY_ROLE_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
        ('Child', 'Child'),
        ('Other', 'Other'),
    ]
    family_role = models.CharField(max_length=20, choices=FAMILY_ROLE_CHOICES)

    # 40) When you get sick... (Use traditional herbs, Go to hospital, Clinic, Other)
    HEALTHCARE_CHOICES = [
        ('Use traditional herbs', 'Use traditional herbs'),
        ('Go to hospital', 'Go to hospital'),
        ('Clinic', 'Clinic'),
        ('Other', 'Other'),
    ]
    healthcare_access = models.CharField(max_length=50, choices=HEALTHCARE_CHOICES)

    # 41) Are you a community leader? (Yes/No => Boolean)
    community_leader = models.BooleanField(default=False)

    # 42) Do you have a vision? (Yes/No => Boolean)
    has_vision = models.BooleanField(default=False)

    # 43) If Yes, What is your vision? (Text)
    vision_description = models.TextField(blank=True, null=True)

    # 44) Specify 5 young people you will train after your training (1...5 => stored in one field or separate fields)
    mentees = models.TextField(
        blank=True,
        null=True,
        help_text="Enter 5 names, one per line or separated by commas."
    )

    # 45) Name of Artisan/Agribusiness Practitioner => a trainer
    assigned_trainer = models.ForeignKey(
        'TrainerApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainees'
    )

    # 46) Name of Epicenter Manager => Must be a user with role='EPICENTER_MANAGER' in the same district?
    epicenter_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='epicenter_trainees'
    )

    # Additional metadata: Cohort, created_by, etc.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainee_applications',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # -----------------------------
    #  NEW FIELDS FOR ASSESSMENT
    # -----------------------------
    STUDY_STATUS_CHOICES = [
        ("NOT_STARTED", "Not Started"),
        ("STARTED_STUDYING", "Started Studying"),
        ("COMPLETED", "Completed"),
        ("DROPPED_OUT", "Dropped Out"),
    ]
    study_status = models.CharField(
        max_length=20,
        choices=STUDY_STATUS_CHOICES,
        default="NOT_STARTED",
        help_text="Tracks the trainee's study progress from not started -> started -> completed or dropped out."
    )

    DIT_CHOICES = [
        ("NOT_REGISTERED", "Not Registered for DIT"),
        ("REGISTERED", "Registered for DIT"),
    ]
    dit_status = models.CharField(
        max_length=15,
        choices=DIT_CHOICES,
        blank=True,
        null=True,
        help_text="Tracks whether the trainee is registered for DIT assessment."
    )

    ASSESSMENT_CHOICES = [
        ("NONE", "No Assessment Yet"),
        ("SUCCESSFUL", "Successfully Assessed"),
        ("UNSUCCESSFUL", "Unsuccessful"),
        ("ABSENT", "Absent"),
    ]
    final_assessment_status = models.CharField(
        max_length=15,
        choices=ASSESSMENT_CHOICES,
        default="NONE",
        help_text="Registrar's final assessment status."
    )

    # Redefine __str__ if you want to keep it at the bottom as well
    def __str__(self):
        return self.applicant_name

    def generate_student_number(self):
        """Generate a unique 4-digit student number."""
        while True:
            number = str(random.randint(1000, 9999))
            if not TraineeApplication.objects.filter(student_number=number).exists():
                return number

    def save(self, *args, **kwargs):
        """Auto-calculate age from date_of_birth and generate student_number."""
        if self.date_of_birth:
            today = timezone.now().date()
            yrs = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                yrs -= 1
            self.age = max(yrs, 0)

        if not self.student_number:
            self.student_number = self.generate_student_number()

        super().save(*args, **kwargs)





































































































































































































































class UnifiedReport(models.Model):
    """
    A single model to handle all report types:
    - STC
    - Requisition
    - Activity
    - Normal Report

    Includes:
    - Status (pending, approved, rejected)
    - Assigned approver (any user except trainers/trainees)
    - Optional multiple viewers (any user except trainers/trainees)
    - Optional reference to previously approved report
    - Optional file upload for attachments
    """

    REPORT_TYPES = [
        ('STC', 'STC'),
        ('REQ', 'Requisition'),
        ('ACT', 'Activity'),
        ('NORM', 'Normal Report'),
    ]
    report_type = models.CharField(
        max_length=4,
        choices=REPORT_TYPES,
        help_text="Type of report (STC, Requisition, Activity, Normal)."
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Optional file upload for the report itself
    report_file = models.FileField(
        upload_to='reports_files/',
        null=True,
        blank=True,
        help_text="Attach any relevant file (PDF, doc, etc.)"
    )

    # For attaching a previously approved report (if desired)
    attached_report = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Optionally attach a previously approved report."
    )

    # Assigned approver (must not be a trainer/trainee)
    assigned_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reports_to_approve',
        limit_choices_to=~Q(role__in=['TRAINER','TRAINEE']),
        help_text="The user responsible for approving/rejecting this report."
    )

    # Viewers: users who can see the report once it is approved
    # (also excludes trainers/trainees)
    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='viewable_reports',
        limit_choices_to=~Q(role__in=['TRAINER','TRAINEE']),
        help_text="Select users who can view this report once approved."
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields to track approval details
    approved_at = models.DateField(null=True, blank=True, help_text="Date when the report was approved")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_reports',
        help_text="User who approved the report"
    )

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"

    def can_view(self, user):
        """
        Checks if a user is allowed to view this report:
         - The creator
         - The assigned approver
         - Any user in the viewers M2M field
        """
        return (
            user == self.created_by
            or user == self.assigned_approver
            or user in self.viewers.all()
        )

    def approve_report(self, user):
        """
        Marks the report as approved by the given user and sets the approved_at date.
        """
        self.status = 'APPROVED'
        self.approved_at = timezone.now().date()  # Store only date
        self.approved_by = user
        self.save()

class ReportComment(models.Model):
    """
    Comments attached to any UnifiedReport.
    Used for approval/rejection notes or general discussion.
    """
    report = models.ForeignKey(
        UnifiedReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.report}"
    



# models.py
class TrainingModule(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(LibraryCategory, on_delete=models.CASCADE)
    file = models.FileField(upload_to='training_modules/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    











































from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SafeguardingMessage(models.Model):
    trainee = models.ForeignKey(TraineeApplication, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)
    read_by = models.ManyToManyField(User, blank=True, related_name='read_messages')
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"





    





















































































































































































































































from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone


class STCReport(models.Model):
    """
    Primary model representing an STC Report.
    This includes the multi-step data:
     - Step 1: assigned_approver, assigned_checker, viewers, etc.
     - Step 2: STC fields (title, output, outcome, current_reality, plus action plan lines).
     - Step 3: Budget lines.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CHECKED', 'Checked'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # Basic
    report_type = models.CharField(max_length=10, default='STC')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    grand_total = models.CharField(max_length=100, blank=True)
    project_name = models.CharField(max_length=255)

    # Who created the report
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stc_prepared_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Approval flow
    assigned_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='stc_reports_to_approve',
        limit_choices_to=~Q(role__in=['TRAINER', 'TRAINEE'])
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='stc_approved_reports'
    )
    approved_at = models.DateField(null=True, blank=True)

    # Checking flow
    assigned_checker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='stc_reports_to_check',
        limit_choices_to=~Q(role__in=['TRAINER', 'TRAINEE'])
    )
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='stc_checked_reports'
    )
    checked_at = models.DateField(null=True, blank=True)

    # Additional viewers who can see the approved report
    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='stc_viewable_reports',
        limit_choices_to=~Q(role__in=['TRAINER', 'TRAINEE'])
    )

    #
    # STC-Specific Fields
    #
    title = models.CharField(max_length=255)
    output = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    current_reality = models.TextField(blank=True)

    def __str__(self):
        return f"STC Report: {self.title}"

    def can_view(self, user):
        """
        A user can view if they are:
         - The person who prepared it
         - The assigned approver
         - The assigned checker
         - In the viewers M2M field
        """
        return (
            user == self.prepared_by
            or user == self.assigned_approver
            or user == self.assigned_checker
            or user in self.viewers.all()
        )

    def approve(self, user):
        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = timezone.now().date()
        self.save()

    def mark_checked(self, user):  # Renamed from check()
        self.status = 'CHECKED'
        self.checked_by = user
        self.checked_at = timezone.now().date()
        self.save()

    def reject(self, comment_text, user):
        """
        Mark as REJECTED, store comment in STCComment with type 'REJECT'.
        """
        self.status = 'REJECTED'
        self.save()
        if comment_text:
            STCComment.objects.create(
                stc_report=self,
                user=user,
                comment=f"[REJECTED] {comment_text}"
            )



class STCActionPlan(models.Model):
    """
    Action plan rows: accountable, action_step, due_date.
    Must be displayed in descending order by due_date.
    """
    stc_report = models.ForeignKey(
        STCReport,
        on_delete=models.CASCADE,
        related_name='action_plans'
    )
    accountable = models.CharField(max_length=255)
    action_step = models.TextField()
    due_date = models.DateField()

    class Meta:
        ordering = ['-due_date']  # from latest to earliest

    def __str__(self):
        return f"{self.accountable} - {self.action_step[:30]}..."


class STCBudgetLine(models.Model):
    """
    Budget rows: specification, meals & refreshment, accommodation, amount, frequency, total
    """
    stc_report = models.ForeignKey(
        STCReport,
        on_delete=models.CASCADE,
        related_name='budget_lines'
    )
    specification = models.CharField(max_length=255)
    meals_and_refreshment = models.CharField(max_length=100, blank=True)
    accommodation = models.CharField(max_length=100, blank=True)
    amount = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    total = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Budget: {self.specification}"


class STCComment(models.Model):
    """
    Stores comments (approval, rejection, general notes).
    """
    stc_report = models.ForeignKey(
        STCReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.stc_report}"




































from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone


class ActivityReport(models.Model):
    """
    Activity Report model:
      - Basic approval flow (no checker)
      - Fields from the screenshot (project_name, title, date, etc.)
      - Status workflow: PENDING -> APPROVED or REJECTED
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    report_type = models.CharField(max_length=10, default='ACTIVITY')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    # Who prepared the report
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_prepared_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Approver
    assigned_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_reports_to_approve',
        limit_choices_to=~Q(role__in=['TRAINER','TRAINEE'])
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_approved_reports'
    )
    approved_at = models.DateField(null=True, blank=True)

    # Viewers
    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='activity_viewable_reports',
        limit_choices_to=~Q(role__in=['TRAINER','TRAINEE'])
    )

    # Activity-specific fields
    project_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True, help_text="Date of the activity")
    venue = models.CharField(max_length=255, blank=True)
    purpose = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    key_activities_conducted = models.TextField(blank=True)
    results_of_activity_findings = models.TextField(blank=True)
    emerging_issues_key_lesson = models.TextField(blank=True)
    challenges_and_mitigation = models.TextField(blank=True)
    key_actions_recommendations = models.TextField(blank=True)

    def __str__(self):
        return f"Activity Report: {self.title}"

    def can_view(self, user):
        return (
            user == self.prepared_by
            or user == self.assigned_approver
            or user in self.viewers.all()
        )

    def approve(self, user):
        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = timezone.now().date()
        self.save()

    def reject(self, comment_text, user):
        self.status = 'REJECTED'
        self.save()
        if comment_text:
            ActivityComment.objects.create(
                activity_report=self,
                user=user,
                comment=f"[REJECTED] {comment_text}"
            )


class ActivityComment(models.Model):
    """
    Comments for Activity Reports (approval notes, rejections, general discussion).
    """
    activity_report = models.ForeignKey(
        ActivityReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.activity_report}"
    

class ActivityMedia(models.Model):
    """
    Stores media files related to an Activity Report.
    """
    activity_report = models.ForeignKey(
        'ActivityReport',
        on_delete=models.CASCADE,
        related_name='media_files'  # ✅ Ensures activity.media_files.all() works
    )
    file = models.FileField(upload_to='activity_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for {self.activity_report.title}"

    



































































































from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

class LeaveReport(models.Model):
    """
    A model representing the Leave Form workflow, similar to STCReport.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # Basic flow fields
    report_type = models.CharField(max_length=20, default='LEAVE')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='PENDING'
    )

    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_prepared_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    assigned_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='leave_reports_to_approve',
        limit_choices_to=~Q(role__in=['TRAINER','TRAINEE'])
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='leave_approved_reports'
    )
    approved_at = models.DateField(null=True, blank=True)

    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='leave_viewable_reports',
        limit_choices_to=~Q(role__in=['TRAINER','TRAINEE'])
    )

    #
    # Leave-specific fields
    #
    LEAVE_TYPE_CHOICES = [
        ('Annual', 'Annual'),
        ('Sick', 'Sick'),
        ('Maternity/Paternity', 'Maternity/Paternity'),
        ('Study', 'Study'),
        ('Sabbatical', 'Sabbatical'),
        ('Other', 'Other'),
    ]

    type_of_leave = models.CharField(max_length=255, blank=True, help_text="Comma-separated leave types chosen")
    other_leave_text = models.CharField(max_length=255, blank=True, help_text="If 'Other' is chosen")

    previous_allocation = models.CharField(max_length=100, blank=True)
    taken = models.CharField(max_length=100, blank=True)
    remaining = models.CharField(max_length=100, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_days = models.IntegerField(editable=False, null=True, blank=True)  # Auto-calculated field
    resuming_work_day = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Auto-calculate total_days before saving.
        """
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError("End date cannot be before start date.")
            self.total_days = (self.end_date - self.start_date).days + 1  # Include start date
        else:
            self.total_days = None  # Reset if dates are missing
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Leave Report ({self.start_date} - {self.end_date})"

    def approve(self, user):
        """ Mark as approved. """
        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = now().date()
        self.save()

    def reject(self, comment_text, user):
        """ Mark as REJECTED, optionally store a rejection comment. """
        self.status = 'REJECTED'
        self.save()
        if comment_text:
            LeaveComment.objects.create(
                leave_report=self,
                user=user,
                comment=f"[REJECTED] {comment_text}"
            )
    def can_view(self, user):
        """ Check if user is prepared_by, assigned_approver, or in viewers. """
        return (
            user == self.prepared_by
            or user == self.assigned_approver
            or user in self.viewers.all()
        )



class LeaveComment(models.Model):
    """
    Comments for the leave form (reject, general remarks, etc.).
    """
    leave_report = models.ForeignKey(
        LeaveReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on LeaveReport {self.leave_report.id}"
