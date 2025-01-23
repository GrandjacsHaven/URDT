from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import CheckboxSelectMultiple
from .models import (
    CustomUser, 
    Phase, 
    Sector,
    Occupation, 
    District, 
    CustomUser, 
    Document, 
    TraineeApplication,
    ActivityReport,
    TrainerApplication,
    Cohort,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment
    ) 
from django.contrib.auth.forms import UserChangeForm

class UserCreationForm(BaseUserCreationForm):
    designation = forms.ChoiceField(
        choices=[],  # Dynamic choices
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(BaseUserCreationForm.Meta):
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'role', 'designation', 'sector', 'district', 
            'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['designation'].choices = []
        self.fields['sector'].queryset = Sector.objects.all()
        self.fields['district'].queryset = District.objects.all()

        if 'role' in self.data:
            role = self.data.get('role')
            self.fields['designation'].choices = self.get_designation_choices(role)

            # Update field requirements and availability based on role
            if role == 'EPICENTER_MANAGER':
                self.fields['district'].required = True
            elif role == 'SECTOR_LEAD':
                self.fields['sector'].required = True
                self.fields['district'].widget.attrs['disabled'] = True  # Disable district field

    def get_designation_choices(self, role):
        role_designation_map = {
            'SUB_ADMIN': [
                'Project Manager', 'CEO', 'Director Education and Training',
                'Director Finance and Admin', 'Director Epicentre Strategy',
                'Director Cooperate Relations', 'Academic Registrar', 'Human Resource', 'Safe Guarding Officer',
            ],
            'ADMINISTRATIVE_USER': ['M&E Officer', 'MERL Coordinator', 'IT Officer'],
        }
        return [(d, d) for d in role_designation_map.get(role, [])]

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')

        # Assign sector or district based on role
        if role == 'EPICENTER_MANAGER':
            user.district = self.cleaned_data.get("district")
        elif role == 'SECTOR_LEAD':
            user.district = None  # Ensure district is not saved for sector leads
            user.sector = self.cleaned_data.get("sector")

        if commit:
            user.save()
        return user





# User Update Form
class UserUpdateForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ['username', 'email', 'role', 'designation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['designation'].choices = []

        if 'role' in self.data:
            role = self.data.get('role')
            self.fields['designation'].choices = self.get_designation_choices(role)

    def get_designation_choices(self, role):
        # Dynamic designation options based on the role
        role_designation_map = {
            'ADMINISTRATIVE_USER': ['M&E Officer', 'Principal', 'Academic Registrar', 'Communications Officer'],
            'TRAINEE': ['General'],
            'SUPER_USER': ['Super user'],
        }
        return [(d, d) for d in role_designation_map.get(role, ['General'])]


# Phase Form
class PhaseForm(forms.ModelForm):
    class Meta:
        model = Phase
        fields = ['name']

# Sector Form
class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['name', 'trainer_designation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer_designation'].required = True

# Occupation Form
class OccupationForm(forms.ModelForm):
    class Meta:
        model = Occupation
        fields = ['sector', 'name']

# District Form
class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['name']

# Document Upload Form
class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file', 'designation']  # Updated 'department' to 'designation'

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = ['phase', 'name']














class ActivityReportForm(forms.ModelForm):
    class Meta:
        model = ActivityReport
        fields = ['title', 'description']







    




































class TraineeProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TraineeApplication
        fields = ["phone_contact", "employment_status"]
        widgets = {
            "phone_contact": forms.TextInput(attrs={"placeholder": "Enter updated phone number"}),
            "employment_status": forms.Select(attrs={"class": "form-control"}),
        }





























class LibraryCategoryForm(forms.ModelForm):
    class Meta:
        model = LibraryCategory
        fields = ['name']


class LibraryDocumentForm(forms.ModelForm):
    class Meta:
        model = LibraryDocument
        fields = ['category', 'title', 'file']





# Example form to update can_enroll_trainees / can_enroll_trainers
# We'll use this in "manage enrollment access"
class EnrollmentAccessForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['can_enroll_trainees', 'can_enroll_trainers']











































































class TrainerApplicationForm(forms.ModelForm):
    # Additional fields
    username = forms.CharField(max_length=150, label="Username", required=True)
    email = forms.EmailField(label="Email Address", required=True)
    first_name = forms.CharField(max_length=30, label="First Name", required=True)
    last_name = forms.CharField(max_length=30, label="Last Name", required=True)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=True,
        help_text="Enter the password for the trainer."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=True,
        help_text="Re-enter the password to confirm."
    )

    designation = forms.ChoiceField(
        choices=[("Artisan", "Artisan"), ("Agribusiness Practitioner", "Agribusiness Practitioner")],
        label="Designation",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control", "id": "id_date_of_birth"}),
        required=True
    )

    age = forms.CharField(
        label="Age",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly", "class": "form-control", "id": "id_age"})
    )

    current_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Enter current location"})
    )

    class Meta:
        model = TrainerApplication
        fields = [
            'passport_photo', 'name', 'phone_contact', 'gender', 'date_of_birth', 'age',
            'marital_status', 'has_smartphone', 'business_name', 'legal_status', 'account_name',
            'account_number', 'monthly_income', 'location', 'household_number', 'zone',
            'block_number', 'nationality', 'pwd', 'nature_of_disability', 'education_level',
            'religion', 'other_religion', 'village', 'parish', 'subcounty', 'sector', 'occupation',
            'designation', 'username', 'email', 'first_name', 'last_name', 'password1', 'password2',
            'current_location', 'district'
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            if user.role == 'EPICENTER_MANAGER' and user.district:
                # Ensure 'district' exists before querying
                self.fields['district'].queryset = District.objects.filter(id=user.district.id)
                self.fields['district'].initial = user.district
                self.fields['district'].disabled = True  # Make it readonly for epicenter managers
            else:
                self.fields['district'].queryset = District.objects.all()  # Show all districts for other users

        self.fields['sector'].queryset = Sector.objects.none()
        self.fields['occupation'].queryset = Occupation.objects.none()

        if 'designation' in self.data:
            designation = self.data.get('designation')
            self.fields['sector'].queryset = Sector.objects.filter(trainer_designation=designation)

        if 'sector' in self.data:
            try:
                sector_id = int(self.data.get('sector'))
                self.fields['occupation'].queryset = Occupation.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.sector:
            self.fields['occupation'].queryset = Occupation.objects.filter(sector=self.instance.sector)



    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    






















































































class TraineeApplicationForm(forms.ModelForm):
    # 2) Username
    username = forms.CharField(max_length=150, label="Username", required=True)
    # 3) Email Address
    email = forms.EmailField(label="Email Address", required=True)
    # 4) First Name
    first_name = forms.CharField(max_length=30, label="First Name", required=True)
    # 5) Last Name
    last_name = forms.CharField(max_length=30, label="Last Name", required=True)
    # 6) Password
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    # 7) Confirm Password
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)

    PWD_CHOICES = [
        ('False', 'No'),
        ('True', 'Yes'),
    ]
    pwd = forms.ChoiceField(
        label="PWD",
        choices=PWD_CHOICES,
        required=True,
        help_text="Is the applicant a person with a disability?"
    )

    ASSETS_CHOICES = [
        ("Motorcycle", "Motorcycle"),
        ("Bicycle", "Bicycle"),
        ("Motor Vehicle", "Motor Vehicle"),
        ("Television", "Television"),
        ("Land", "Land"),
        ("Permanent House", "Permanent House"),
        ("Others", "Others"),
    ]
    other_assets_multi = forms.MultipleChoiceField(
        label="Which other assets do you currently own?",
        required=False,
        widget=CheckboxSelectMultiple,
        choices=ASSETS_CHOICES
    )

    current_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Enter current location"})
    )

    cohort = forms.ModelChoiceField(
            queryset=Cohort.objects.all(),
            required=False,
            label="Assign to Cohort",
            widget=forms.Select(attrs={'class': 'form-control'})
        )

    class Meta:
        model = TraineeApplication
        fields = [
            "passport_photo", "training_year_month", "applicant_name", "phone_contact",
            "phone_ownership", "gender", "date_of_birth", "age", "consent_form_obtained",
            "marital_status", "household_number", "zone", "block_number", "village", "parish",
            "subcounty", "nationality", "pwd", "nature_of_disability", "education_level",
            "religion", "employment_status", "monthly_income", "sector", "occupation",
            "has_smartphone", "household_members_above_15", "meals_per_day", "internet_access",
            "online_platform_awareness", "family_role", "healthcare_access", "community_leader",
            "has_vision", "vision_description", "mentees", "assigned_trainer", "epicenter_manager",
            "current_location",'district','cohort'
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "age": forms.NumberInput(attrs={"readonly": True}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        user = None
        if self.request and self.request.user.is_authenticated:
            user = self.request.user

        # Fix district field to the epicenter manager's assigned district
        if user and user.role == 'EPICENTER_MANAGER' and user.district:
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True  # Make it readonly for epicenter managers

            # Fix epicenter manager field to the logged-in user
            self.fields['epicenter_manager'].queryset = CustomUser.objects.filter(id=user.id)
            self.fields['epicenter_manager'].initial = user
            self.fields['epicenter_manager'].disabled = True

        # Populate sector and occupation normally
        self.fields["sector"].queryset = Sector.objects.all()
        self.fields["occupation"].queryset = Occupation.objects.none()

        # Handle occupation queryset based on sector selection
        if "sector" in self.data:
            try:
                sector_id = int(self.data.get("sector"))
                self.fields["occupation"].queryset = Occupation.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                self.fields["occupation"].queryset = Occupation.objects.none()
        elif self.instance.pk and self.instance.sector:
            self.fields["occupation"].queryset = Occupation.objects.filter(sector=self.instance.sector)

        # Handle assigned trainer queryset based on selected sector and occupation within fixed district
        if user and user.role == 'EPICENTER_MANAGER' and user.district:
            fixed_district = user.district

            if "sector" in self.data and "occupation" in self.data:
                try:
                    sector_id = int(self.data.get("sector"))
                    occupation_id = int(self.data.get("occupation"))
                    self.fields["assigned_trainer"].queryset = TrainerApplication.objects.filter(
                        district=fixed_district, sector_id=sector_id, occupation_id=occupation_id
                    )
                except (ValueError, TypeError):
                    self.fields["assigned_trainer"].queryset = TrainerApplication.objects.none()
            elif self.instance.pk and self.instance.sector and self.instance.occupation:
                self.fields["assigned_trainer"].queryset = TrainerApplication.objects.filter(
                    district=fixed_district, sector=self.instance.sector, occupation=self.instance.occupation
                )
            else:
                self.fields["assigned_trainer"].queryset = TrainerApplication.objects.none()

        # Handle epicenter manager selection based on district (for other roles)
        if "district" in self.data:
            try:
                district_id = int(self.data.get("district"))
                self.fields["epicenter_manager"].queryset = CustomUser.objects.filter(
                    role='EPICENTER_MANAGER', district_id=district_id
                )
            except (ValueError, TypeError):
                self.fields["epicenter_manager"].queryset = CustomUser.objects.filter(role='EPICENTER_MANAGER')
        elif self.instance.pk and self.instance.district:
            self.fields["epicenter_manager"].queryset = CustomUser.objects.filter(
                role='EPICENTER_MANAGER', district=self.instance.district
            )
        else:
            self.fields["epicenter_manager"].queryset = CustomUser.objects.filter(role='EPICENTER_MANAGER')





    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def clean(self):
        cleaned_data = super().clean()
        pwd_str = cleaned_data.get('pwd')
        cleaned_data['pwd'] = (pwd_str == 'True')
        chosen_assets = cleaned_data.get('other_assets_multi', [])
        cleaned_data['other_assets'] = ", ".join(chosen_assets)
        return cleaned_data


































































from django.contrib.auth import get_user_model
User = get_user_model()

class UnifiedReportForm(forms.ModelForm):
    """
    Handles submission of a new UnifiedReport or editing an existing one.
    Exposes:
      - report_type (STC, Requisition, Activity, Normal)
      - title, description
      - file upload
      - optional link to previously approved report
      - assigned_approver
      - viewers (multiple)
    """

    # Show all users except trainers/trainees
    # for the assigned_approver and viewers
    assigned_approver = forms.ModelChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=False,
        label="Assign Approver"
    )
    viewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=False,
        widget=CheckboxSelectMultiple,
        label="Select Viewers (who can view once approved)"
    )

    class Meta:
        model = UnifiedReport
        fields = [
            'report_type',
            'title',
            'description',
            'report_file',
            'attached_report',
            'assigned_approver',
            'viewers'
        ]
        labels = {
            'report_type': 'Report Type',
            'title': 'Report Title',
            'description': 'Description',
            'report_file': 'Upload File (optional)',
            'attached_report': 'Attach Previously Approved Report (optional)'
        }

class ReportCommentForm(forms.ModelForm):
    """
    Simple form to add a new comment to any report.
    """
    class Meta:
        model = ReportComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3}),
        }
        labels = {
            'comment': 'Add a Comment'
        }






class TraineeProfileUpdateForm(forms.ModelForm):
    """
    Fields the epicenter manager is allowed to update: phone_contact, monthly_income, current_location
    """
    class Meta:
        model = TraineeApplication
        fields = ['phone_contact', 'monthly_income', 'current_location']


class TrainerProfileUpdateForm(forms.ModelForm):
    """
    Fields the epicenter manager can update: phone_contact, monthly_income, location, education_level
    We'll override education_level to be a text input if needed,
    or keep it as a dropdown if your model has choices.
    """
    education_level = forms.CharField(required=False, label="Education Level",
        widget=forms.TextInput(attrs={"placeholder": "Update education level"})
    )

    class Meta:
        model = TrainerApplication
        fields = ['phone_contact', 'monthly_income', 'location', 'education_level']