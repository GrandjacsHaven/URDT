from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
import uuid  # For possible unique IDs

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
    can_enroll_trainees = models.BooleanField(default=False, help_text="Can enroll trainees")
    can_enroll_trainers = models.BooleanField(default=False, help_text="Can enroll trainers")

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
    






















    #*Administrative User related models*#

# Activity Plan Model
class ActivityPlan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.name

# report Model    
class Report(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='reports/')
    designation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Relevant Data Model 
class RelevantData(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    designation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Document Model
class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    designation = models.CharField(max_length=255)  
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

#Activity report Model
class ActivityReport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_submitted = models.DateField(auto_now_add=True)
    epicenter_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_reports",
    )
    approved = models.BooleanField(default=False)  # Approval status

    def __str__(self):
        return f"{self.title} by {self.epicenter_manager.username}"



    

















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
        Cohort, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="trainees",
        help_text="Select the cohort for this trainee"
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
    gender = models.CharField(max_length=30)

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
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)

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
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='trainee_sector')

    # 32) Occupation (Dropdown under the selected sector)
    occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='trainee_occupation')

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
        TrainerApplication,
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

    def __str__(self):
        return self.applicant_name

    def save(self, *args, **kwargs):
        """Auto-calculate age from date_of_birth."""
        if self.date_of_birth:
            today = timezone.now().date()
            yrs = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                yrs -= 1
            self.age = max(yrs, 0)
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