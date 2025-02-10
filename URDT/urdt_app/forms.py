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
    TrainerApplication,
    Cohort,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment,
    TrainingModule,
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
            elif role == 'DATA_ENTRANT':
                self.fields['district'].required = True
            elif role == 'SECTOR_LEAD':
                self.fields['sector'].required = True
                self.fields['district'].widget.attrs['disabled'] = True  # Disable district field

    def get_designation_choices(self, role):
        role_designation_map = {
            'SUB_ADMIN': [
                'Project Manager', 'CEO', 'Director Education and Training',
                'Director Finance and Admin', 'Director Epicentre Strategy',
                'Director Cooperate Relations', 'Academic Registrar', 'Human Resource', 'Safe Guarding Officer','Principal','Accountant'
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
        elif role == 'DATA_ENTRANT':
            user.district = self.cleaned_data.get("district")
        elif role == 'SECTOR_LEAD':
            user.district = None  # Ensure district is not saved for sector leads
            user.sector = self.cleaned_data.get("sector")

        if commit:
            user.save()
        return user





# User Update Form

class UserUpdateForm(UserChangeForm):
    password1 = forms.CharField(
        label="New Password", 
        widget=forms.PasswordInput, 
        required=False,
        help_text="Leave blank to keep the current password."
    )
    password2 = forms.CharField(
        label="Confirm New Password", 
        widget=forms.PasswordInput, 
        required=False,
        help_text="Leave blank to keep the current password."
    )
    
    designation = forms.ChoiceField(
        choices=[],  # Dynamic choices based on role
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
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

        if self.instance:
            role = self.instance.role
            self.fields['designation'].choices = self.get_designation_choices(role)

            # Apply constraints based on role
            if role == 'EPICENTER_MANAGER':
                self.fields['district'].required = True
            elif role == 'DATA_ENTRANT':
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

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')

        # Assign sector or district based on role
        if role == 'EPICENTER_MANAGER':
            user.district = self.cleaned_data.get("district")
        elif role == 'DATA_ENTRANT':
            user.district = self.cleaned_data.get("district")
        elif role == 'SECTOR_LEAD':
            user.district = None  # Ensure district is not saved for sector leads
            user.sector = self.cleaned_data.get("sector")

        # Only update password if a new one is provided
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


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

class OccupationeForm(forms.ModelForm):
    class Meta:
        model = Occupation
        fields = ['name']

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
        fields = ['name']






















    




































class TraineeProfileUpdateForm(forms.ModelForm):
    """
    Fields the trainee can update: contact, location, employment_status, monthly_income
    (Assuming we store these in the TraineeApplication or the user itself).
    """
    class Meta:
        model = TraineeApplication
        fields = [
            'phone_contact',
            'current_location',
            'employment_status',
            'monthly_income'
        ]































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
    # Additional fields (unchanged)
    username = forms.CharField(max_length=150, label="Username", required=True)
    email = forms.EmailField(label="Email Address", required=True)
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
            'designation', 'username', 'email', 'password1', 'password2',
            'current_location', 'district'
        ]

    def __init__(self, *args, **kwargs):
        # Pop the request so that we have access to the logged-in user.
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        user = None
        if self.request and self.request.user.is_authenticated:
            user = self.request.user

        # Configure district field for epicenter managers
        if user and user.role == 'EPICENTER_MANAGER' and user.district:
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True  # Make it read-only for epicenter managers
        else:
            self.fields['district'].queryset = District.objects.all()

        # For sector leads, fix the sector and designation fields.
        if user and user.role == 'SECTOR_LEAD' and user.sector:
            # Fix the sector field to the logged-in user's sector.
            self.fields['sector'].queryset = Sector.objects.filter(id=user.sector.id)
            self.fields['sector'].initial = user.sector
            self.fields['sector'].disabled = True

            # Fix the designation field to the sector's trainer designation.
            fixed_designation = user.sector.trainer_designation
            self.fields['designation'].initial = fixed_designation
            self.fields['designation'].disabled = True  # Prevent editing

            # Optionally, restrict the choices so only the fixed designation is available.
            self.fields['designation'].choices = [(fixed_designation, fixed_designation)]
        else:
            self.fields['sector'].queryset = Sector.objects.all()

        # Populate occupations based on sector selection.
        self.fields['occupation'].queryset = Occupation.objects.none()
        if 'sector' in self.data:
            try:
                sector_id = int(self.data.get('sector'))
                self.fields['occupation'].queryset = Occupation.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.sector:
            self.fields['occupation'].queryset = Occupation.objects.filter(sector=self.instance.sector)

        # If the designation is in the POST data (e.g. if not disabled) use it to filter sectors.
        if 'designation' in self.data and not self.fields['designation'].disabled:
            designation = self.data.get('designation')
            self.fields['sector'].queryset = Sector.objects.filter(trainer_designation=designation)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    # Optional: If you use disabled fields, they aren’t submitted by the browser.
    # You can override the clean method to ensure the fixed fields are set.
    def clean(self):
        cleaned_data = super().clean()
        if self.fields['designation'].disabled:
            # Ensure that the fixed designation is included.
            cleaned_data['designation'] = self.fields['designation'].initial
        return cleaned_data


    









class TrainerApplicationEditForm(forms.ModelForm):
    # These fields duplicate the ones in the creation form
    username = forms.CharField(max_length=150, label="Username", required=False,help_text="Leave blank to keep the current username.")
    email = forms.EmailField(label="Email Address", required=False,help_text="Leave blank to keep the current email.")
    # Password fields are now optional during editing:
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )
    
    # The rest of the fields remain exactly as in the creation form:
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
            'designation', 'username', 'email','password1', 'password2',
            'current_location', 'district'
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "age": forms.NumberInput(attrs={"readonly": True}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TrainerApplicationEditForm, self).__init__(*args, **kwargs)
        
        user = None
        if self.request and self.request.user.is_authenticated:
            user = self.request.user

        # If the logged-in user is an Epicenter Manager, restrict district:
        if user and user.role == 'EPICENTER_MANAGER' and user.district:
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True
        else:
            self.fields['district'].queryset = District.objects.all()

        # If the logged-in user is a Sector Lead, restrict sector:
        if user and user.role == 'SECTOR_LEAD' and user.sector:
            self.fields['sector'].queryset = Sector.objects.filter(id=user.sector.id)
            self.fields['sector'].initial = user.sector
            self.fields['sector'].disabled = True
        else:
            self.fields['sector'].queryset = Sector.objects.all()

        # Populate occupations based on the sector selection
        self.fields['occupation'].queryset = Occupation.objects.none()
        if "sector" in self.data:
            try:
                sector_id = int(self.data.get("sector"))
                self.fields['occupation'].queryset = Occupation.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.sector:
            self.fields['occupation'].queryset = Occupation.objects.filter(sector=self.instance.sector)

        # If the form data contains 'designation', filter sectors by trainer designation
        if 'designation' in self.data:
            designation = self.data.get('designation')
            self.fields['sector'].queryset = Sector.objects.filter(trainer_designation=designation)
    
    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        # If no new password is entered, skip password validation.
        if not p1 and not p2:
            return p2
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2
    
    def save(self, commit=True):
        trainer = super(TrainerApplicationEditForm, self).save(commit=False)
        new_password = self.cleaned_data.get("password1")
        if new_password:
            # Update the password on the associated user if provided.
            if hasattr(trainer, 'user') and trainer.user:
                trainer.user.set_password(new_password)
                trainer.user.save()
        if commit:
            trainer.save()
        return trainer


















































































class TraineeApplicationForm(forms.ModelForm):
    # 2) Username
    username = forms.CharField(max_length=150, label="Username", required=True)

    # 3) Email Address
    email = forms.EmailField(label="Email Address", required=True)

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
        queryset=None,  # We will set this in __init__ when we have Cohort objects
        required=False,
        label="Assign to Cohort",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TraineeApplication
        fields = [
      
            "passport_photo", 
            "training_year_month", 
            "applicant_name", 
            "phone_contact",
            "phone_ownership", 
            "gender", 
            "date_of_birth", 
            "age", 
            "consent_form_obtained",
            "marital_status", 
            "household_number", 
            "zone", 
            "block_number", 
            "village", 
            "parish",
            "subcounty", 
            "nationality", 
            "pwd", 
            "nature_of_disability", 
            "education_level",
            "religion", 
            "employment_status", 
            "monthly_income", 
            "sector", 
            "occupation",
            "has_smartphone", 
            "household_members_above_15", 
            "meals_per_day", 
            "internet_access",
            "online_platform_awareness", 
            "family_role", 
            "healthcare_access", 
            "community_leader",
            "has_vision", 
            "vision_description", 
            "mentees", 
            "assigned_trainer", 
            "epicenter_manager",
            "current_location",
            'district',
            'cohort'
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "age": forms.NumberInput(attrs={"readonly": True}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Here you would set cohort's queryset properly
        self.fields['cohort'].queryset = Cohort.objects.all()

        user = None
        if self.request and self.request.user.is_authenticated:
            user = self.request.user

        # Fix district for epicenter manager
        if user and getattr(user, 'role', None) == 'EPICENTER_MANAGER' and getattr(user, 'district', None):
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True

            self.fields['epicenter_manager'].queryset = CustomUser.objects.filter(id=user.id)
            self.fields['epicenter_manager'].initial = user
            self.fields['epicenter_manager'].disabled = True

        elif user and getattr(user, 'role', None) == 'DATA_ENTRANT' and getattr(user, 'district', None):
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True  # Make district field readonly for data entrants

        else:
            self.fields['district'].queryset = District.objects.all()
            self.fields['epicenter_manager'].queryset = CustomUser.objects.filter(role='EPICENTER_MANAGER')

        # Fix sector for sector lead role
        if user and getattr(user, 'role', None) == 'SECTOR_LEAD' and getattr(user, 'sector', None):
            self.fields['sector'].queryset = Sector.objects.filter(id=user.sector.id)
            self.fields['sector'].initial = user.sector
            self.fields['sector'].disabled = True
        else:
            self.fields['sector'].queryset = Sector.objects.all()

        # Populate occupations based on sector selection
        self.fields["occupation"].queryset = Occupation.objects.none()
        if "sector" in self.data:
            try:
                sector_id = int(self.data.get("sector"))
                self.fields["occupation"].queryset = Occupation.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                self.fields["occupation"].queryset = Occupation.objects.none()
        elif self.instance.pk and self.instance.sector:
            self.fields["occupation"].queryset = Occupation.objects.filter(sector=self.instance.sector)

        # Assigned trainer filtering for epicenter manager
        if user and getattr(user, 'role', None) == 'EPICENTER_MANAGER' and getattr(user, 'district', None):
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


class TrainingModuleForm(forms.ModelForm):
    class Meta:
        model = TrainingModule
        fields = ['title', 'category', 'file']
















































































































































from django import forms
from .models import TraineeApplication, SafeguardingMessage

class TraineeProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TraineeApplication
        fields = ['phone_contact', 'current_location', 'employment_status', 'monthly_income']



class SafeguardingMessageForm(forms.ModelForm):
    class Meta:
        model = SafeguardingMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your message...'}),
        }



















































class ManagerTraineeStatusForm(forms.ModelForm):
    """
    For Epicenter Manager: can update study_status and dit_status 
    (depending on the progression).
    """
    class Meta:
        model = TraineeApplication
        fields = ['study_status', 'dit_status']

    def clean(self):
        cleaned_data = super().clean()
        study_status = cleaned_data.get('study_status')
        dit_status = cleaned_data.get('dit_status')

        # Optional: Enforce logic that dit_status can only be set if study_status == "COMPLETED"
        if study_status != "COMPLETED" and dit_status == "REGISTERED":
            self.add_error(
                'dit_status', 
                "You can only register a trainee for DIT if they have 'Completed'."
            )

        return cleaned_data


class RegistrarAssessmentForm(forms.ModelForm):
    """
    For the Academic Registrar to update final_assessment_status.
    """
    class Meta:
        model = TraineeApplication
        fields = ['final_assessment_status']


















































































































































from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import STCReport, STCActionPlan, STCBudgetLine, STCComment

User = get_user_model()


#
# Step 1: Basic STC Info (Approver, Checker, Viewers)
#
class STCBaseInfoForm(forms.ModelForm):
    """
    First step: assign approver, checker, viewers. 
    'report_type' is set to 'STC' by default, hidden or read-only.
    """
    assigned_approver = forms.ModelChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=True,
        label="Select Approver"
    )
    assigned_checker = forms.ModelChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=True,
        label="Select Checker"
    )
    viewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=False,
        label="Select Viewers",
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = STCReport
        fields = ['assigned_approver', 'assigned_checker', 'viewers']


#
# Step 2: STC Fields (Title, Output, Outcome, Current Reality) + Action Plan
#
class STCFieldsForm(forms.ModelForm):
    """
    Second step: STC fields
    """
    class Meta:
        model = STCReport
        fields = ['project_name','title', 'output', 'outcome', 'current_reality']
        labels = {
            'project_name': 'Project Name',
            'title': 'Title',
            'output': 'Output',
            'outcome': 'Outcome',
            'current_reality': 'Current Reality',
        }


class STCActionPlanForm(forms.ModelForm):
    class Meta:
        model = STCActionPlan
        fields = ['accountable', 'action_step', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date'})
        }


STCActionPlanFormSet = inlineformset_factory(
    STCReport, STCActionPlan, 
    form=STCActionPlanForm,
    extra=1,
    can_delete=True
)


#
# Step 3: Budget lines
#
class STCBudgetLineForm(forms.ModelForm):
    class Meta:
        model = STCBudgetLine
        fields = ['specification', 'meals_and_refreshment', 'accommodation',
                  'amount', 'frequency', 'total']


STCBudgetFormSet = inlineformset_factory(
    STCReport, STCBudgetLine,
    form=STCBudgetLineForm,
    extra=1,
    can_delete=True
)


#
# Comments
#
class STCCommentForm(forms.ModelForm):
    class Meta:
        model = STCComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3})
        }
        labels = {
            'comment': 'Add Comment'
        }


class STCGrandTotalForm(forms.ModelForm):
    class Meta:
        model = STCReport
        fields = ['grand_total']


























from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import ActivityReport, ActivityComment, ActivityMedia

User = get_user_model()


#
# STEP 1: Basic Info (Approver, Viewers) - No Checker for Activity
#
class ActivityBaseInfoForm(forms.ModelForm):
    assigned_approver = forms.ModelChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=True,
        label="Select Approver"
    )
    viewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=False,
        label="Select Viewers",
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ActivityReport
        fields = ['assigned_approver', 'viewers']


#
# STEP 2: Activity Fields
#
class ActivityFieldsForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = ActivityReport
        fields = [
            'project_name', 'title', 'date', 'venue', 'purpose', 'outcome',
            'key_activities_conducted', 'results_of_activity_findings',
            'emerging_issues_key_lesson', 'challenges_and_mitigation',
            'key_actions_recommendations'
        ]




#
# Comments
#
class ActivityCommentForm(forms.ModelForm):
    class Meta:
        model = ActivityComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3})
        }
        labels = {
            'comment': 'Add a Comment'
        }



























































from django import forms
from django.forms import CheckboxSelectMultiple
from .models import TraineeApplication, Cohort, District, Sector, Occupation, CustomUser, TrainerApplication

class TraineeApplicationEditForm(forms.ModelForm):
    # Duplicate the fields used during creation:
    username = forms.CharField(max_length=150, label="Username",required=False,
        help_text="Leave blank to keep the current username.")
    email = forms.EmailField(label="Email Address", required=False,
        help_text="Leave blank to keep the current email.")
    # Password fields are now optional
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )
    
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
            "current_location", "district", "cohort",
            "username", "email", "password1", "password2"
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "age": forms.NumberInput(attrs={"readonly": True}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TraineeApplicationEditForm, self).__init__(*args, **kwargs)
        
        # The following logic is identical to the creation form
        user = None
        if self.request and self.request.user.is_authenticated:
            user = self.request.user

        if user and user.role == 'DATA_ENTRANT' and user.district:
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True  # Make it readonly for data entrants

        # Fix district for epicenter manager
        if user and user.role == 'EPICENTER_MANAGER' and user.district:
            self.fields['district'].queryset = District.objects.filter(id=user.district.id)
            self.fields['district'].initial = user.district
            self.fields['district'].disabled = True  # Make it readonly for epicenter managers
            self.fields['epicenter_manager'].queryset = CustomUser.objects.filter(id=user.id)
            self.fields['epicenter_manager'].initial = user
            self.fields['epicenter_manager'].disabled = True
        else:
            self.fields['district'].queryset = District.objects.all()
            self.fields['epicenter_manager'].queryset = CustomUser.objects.filter(role='EPICENTER_MANAGER')
        
        # Fix sector for sector lead role
        if user and user.role == 'SECTOR_LEAD' and user.sector:
            self.fields['sector'].queryset = Sector.objects.filter(id=user.sector.id)
            self.fields['sector'].initial = user.sector
            self.fields['sector'].disabled = True  # Lock sector to sector lead's assigned sector
        else:
            self.fields['sector'].queryset = Sector.objects.all()
        
        # Populate occupations based on sector selection
        self.fields["occupation"].queryset = Occupation.objects.none()
        if "sector" in self.data:
            try:
                sector_id = int(self.data.get("sector"))
                self.fields["occupation"].queryset = Occupation.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                self.fields["occupation"].queryset = Occupation.objects.none()
        elif self.instance.pk and self.instance.sector:
            self.fields["occupation"].queryset = Occupation.objects.filter(sector=self.instance.sector)
        
        # Assigned trainer filtering for epicenter manager
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
        # If no new password is provided, skip validation
        if not p1 and not p2:
            return p2
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2
    
    def save(self, commit=True):
        trainee = super(TraineeApplicationEditForm, self).save(commit=False)
        new_password = self.cleaned_data.get("password1")
        if new_password:
            # Assuming that the TraineeApplication is linked to a CustomUser instance via a one-to-one field named "user".
            # Adjust accordingly if your model structure differs.
            if hasattr(trainee, 'user') and trainee.user:
                trainee.user.set_password(new_password)
                trainee.user.save()
        if commit:
            trainee.save()
        return trainee





































































from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import LeaveReport, LeaveComment

User = get_user_model()


#
# Step 1: Approver, Checker, Viewers
#
class LeaveBaseInfoForm(forms.ModelForm):
    """
    Step 1: Choose approver and viewers for a Leave form.
    """
    assigned_approver = forms.ModelChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=True,
        label="Select Approver"
    )

    viewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(role__in=['TRAINER','TRAINEE']),
        required=False,
        label="Select Viewers",
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = LeaveReport
        fields = ['assigned_approver', 'viewers']


#
# Step 2: Actual Leave Fields
#
LEAVE_TYPE_CHOICES = [
    ('Annual', 'Annual'),
    ('Sick', 'Sick'),
    ('Maternity/Paternity', 'Maternity/Paternity'),
    ('Study', 'Study'),
    ('Sabbatical', 'Sabbatical'),
    ('Other', 'Other'),
]

class LeaveFieldsForm(forms.ModelForm):
    """
    Form to capture the various fields for the Leave request.
    We'll handle type_of_leave as multiple checkboxes + an 'other' text.
    """
    type_of_leave = forms.MultipleChoiceField(
        choices=LEAVE_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Type of Leave"
    )
    other_leave_text = forms.CharField(
        required=False,
        label="If Other, Specify"
    )

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)
    resuming_work_day = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)

    class Meta:
        model = LeaveReport
        fields = [
            'type_of_leave', 'other_leave_text',
            'previous_allocation', 'taken', 'remaining',
            'start_date', 'end_date', 'resuming_work_day'  # ❌ Removed 'total_days' 
        ]

    def clean(self):
        cleaned_data = super().clean()
        # Convert type_of_leave list -> comma-separated string
        chosen_types = cleaned_data.get('type_of_leave', [])
        if chosen_types:
            cleaned_data['type_of_leave'] = ",".join(chosen_types)
        else:
            cleaned_data['type_of_leave'] = ""
        return cleaned_data



class LeaveCommentForm(forms.ModelForm):
    class Meta:
        model = LeaveComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3})
        }
        labels = {
            'comment': 'Add Comment'
        }
