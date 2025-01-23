from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from .utils import administrative_user_required, superuser_required, sub_admin_required, epicenter_manager_required,sector_lead_required,trainer_required,trainee_required
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import (
    CustomUser, 
    Phase, 
    Sector, 
    Cohort, 
    District, 
    Occupation, 
    TraineeApplication,
    TrainerApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument
)
from .forms import (
    UserCreationForm, 
    UserUpdateForm,
    PhaseForm,
    SectorForm,
    OccupationForm,
    DistrictForm,
    TraineeApplicationForm,
    TrainerApplicationForm,
    LibraryCategoryForm,
    LibraryDocumentForm,
    EnrollmentAccessForm
)


# Login View
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == "SUPER_USER":
            return redirect("superuser_dashboard")
        elif request.user.role == "ADMINISTRATIVE_USER":
            return redirect("administrativeuser_dashboard")
        elif request.user.role == "SUB_ADMIN":
            return redirect("subadmin_dashboard")
        elif request.user.role == "EPICENTER_MANAGER":
            return redirect("epicenter_manager_dashboard")
        elif request.user.role == "SECTOR_LEAD":
            return redirect("sector_lead_dashboard")
        elif request.user.role == "TRAINER":
            return redirect("trainer_dashboard")
        elif request.user.role == "TRAINEE":
            return redirect("trainee_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == "SUPER_USER":
                return redirect("superuser_dashboard")
            elif user.role == "ADMINISTRATIVE_USER":
                return redirect("administrativeuser_dashboard")
            elif user.role == "SUB_ADMIN":
                return redirect("subadmin_dashboard")
            elif user.role == "EPICENTER_MANAGER":
                return redirect("epicenter_manager_dashboard")
            elif user.role == "SECTOR_LEAD":
                return redirect("sector_lead_dashboard")
            elif user.role == "TRAINER":
                return redirect("trainer_dashboard")
            elif user.role == "TRAINEE":
                return redirect("trainee_dashboard")
        # else: possibly show form errors
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})



# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")


















# Superuser Views
# Superuser Dashboard
@login_required
@user_passes_test(superuser_required)
def superuser_dashboard(request):
    """
    1) The dashboard:
       For now, just show the list of all users.
       Subject to change as needed.
    """
    users = CustomUser.objects.all().order_by('username')
    context = {
        'users': users,
    }
    return render(request, 'superuser/dashboard.html', context)


#manage users
@login_required
@user_passes_test(superuser_required)
def manage_users(request):
    """
    2) Manage users: show existing users (except trainers, trainees).
       Provide a 'Create User' button.
    """
    # Exclude roles 'TRAINER' and 'TRAINEE'
    users = CustomUser.objects.exclude(role__in=['TRAINER', 'TRAINEE']).order_by('username')
    return render(request, 'superuser/manage_users.html', {'users': users})

# Create User
@login_required
@user_passes_test(superuser_required)
def create_user_view(request):
    """
    Create a new user (excluding trainers and trainees).
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role in ['TRAINER', 'TRAINEE']:
                return redirect('manage_users')
            user.save()
            return redirect('manage_users')
    else:
        form = UserCreationForm()

    return render(request, 'superuser/create_user.html', {'form': form})


#manage phases
@login_required
@user_passes_test(superuser_required)
def manage_phases(request):
    """
    3) Manage phases: show existing phases & add a new phase.
       Also show a button to add cohorts for each phase.
    """
    phases = Phase.objects.all().order_by('id')

    if request.method == 'POST':
        phase_form = PhaseForm(request.POST)
        if phase_form.is_valid():
            phase_form.save()
            return redirect('manage_phases')
    else:
        phase_form = PhaseForm()

    context = {
        'phases': phases,
        'phase_form': phase_form,
    }
    return render(request, 'superuser/manage_phases.html', context)

# Add Cohort
@login_required
@user_passes_test(superuser_required)
def add_cohort(request, phase_id):
    """
    3b) Add a Cohort under a specific Phase.
    """
    phase = get_object_or_404(Phase, id=phase_id)
    if request.method == 'POST':
        cohort_name = request.POST.get('cohort_name')
        if cohort_name:
            Cohort.objects.create(phase=phase, name=cohort_name)
        return redirect('manage_phases')
    return render(request, 'superuser/add_cohort.html', {'phase': phase})


#manage sectors
@login_required
@user_passes_test(superuser_required)
def manage_sectors(request):
    """
    Display the list of existing sectors with related occupations.
    """
    sectors = Sector.objects.prefetch_related('occupations')
    return render(request, 'superuser/manage_sectors.html', {'sectors': sectors})



# Add Sector
@login_required
@user_passes_test(superuser_required)
def add_sector(request):
    """
    Add a sector with a trainer designation.
    """
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_sectors')  # Redirects to sector management
    else:
        form = SectorForm()
    return render(request, 'superuser/add_sector.html', {'form': form})


# Add Occupation
@login_required
@user_passes_test(superuser_required)
def add_occupation(request, sector_id):
    """
    4c) Add occupation under a selected sector.
    """
    sector = get_object_or_404(Sector, id=sector_id)
    if request.method == 'POST':
        occupation_name = request.POST.get('occupation_name')
        if occupation_name:
            Occupation.objects.create(sector=sector, name=occupation_name)
        return redirect('manage_sectors')
    return render(request, 'superuser/add_occupation.html', {'sector': sector})


#manage districts
@login_required
@user_passes_test(superuser_required)
def manage_districts(request):
    """
    5) Manage districts: show existing districts, add new ones.
    """
    districts = District.objects.all().order_by('name')

    if request.method == 'POST':
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_districts')
    else:
        form = DistrictForm()

    context = {
        'districts': districts,
        'form': form
    }
    return render(request, 'superuser/manage_districts.html', context)

#manage trainees
@login_required
@user_passes_test(superuser_required)
def manage_trainees(request):
    """
    6) Show existing trainees and a button to add a trainee.
       Also a button to see "trainee enrollment access".
    """
    trainee_users = CustomUser.objects.filter(role='TRAINEE').order_by('username')
    trainee_apps = TraineeApplication.objects.all().order_by('-created_at')

    return render(request, 'superuser/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
    })




#trainee enrollment access
@login_required
@user_passes_test(superuser_required)
def trainee_enrollment_access(request):
    """
    6c) Show all users except trainers & trainees,
        with a boolean to set can_enroll_trainees.
    """
    users = CustomUser.objects.exclude(role__in=['TRAINER','TRAINEE']).order_by('username')

    if request.method == 'POST':
        for user in users:
            field_name = f'enroll_{user.id}'
            checked = request.POST.get(field_name)
            user.can_enroll_trainees = True if checked == 'on' else False
            user.save()
        return redirect('trainee_enrollment_access')

    return render(request, 'superuser/trainee_enrollment_access.html', {'users': users})

#manage trainers
@login_required
@user_passes_test(superuser_required)
def manage_trainers(request):
    """
    7) Show existing trainers and a button to add a trainer.
       Also a button to see "trainer enrollment" booleans.
    """
    trainer_users = CustomUser.objects.filter(role='TRAINER').order_by('username')
    trainer_apps = TrainerApplication.objects.all().order_by('-created_at')
    return render(request, 'superuser/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
    })






#trainer enrollment access
@login_required
@user_passes_test(superuser_required)
def trainer_enrollment_access(request):
    """
    7c) Show the same set of users (except trainers/trainees)
        with a boolean for can_enroll_trainers.
    """
    users = CustomUser.objects.exclude(role__in=['TRAINER','TRAINEE']).order_by('username')

    if request.method == 'POST':
        for user in users:
            field_name = f'enrolltrainer_{user.id}'
            checked = request.POST.get(field_name)
            user.can_enroll_trainers = True if checked == 'on' else False
            user.save()
        return redirect('trainer_enrollment_access')

    return render(request, 'superuser/trainer_enrollment_access.html', {'users': users})









#library dashboard
@login_required
@user_passes_test(superuser_required)
def library_dashboard(request):
    """
    10) Library page: show docs by category, and allow 
        superuser to create categories and upload documents.
    """
    categories = LibraryCategory.objects.all().order_by('name')
    documents = LibraryDocument.objects.select_related('category').all().order_by('-created_at')
    return render(request, 'superuser/library_dashboard.html', {
        'categories': categories,
        'documents': documents,
    })

# Add Library Category
@login_required
@user_passes_test(superuser_required)
def add_library_category(request):
    """
    Add a new library category. Only superuser sees this link.
    """
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library_dashboard')
    else:
        form = LibraryCategoryForm()
    return render(request, 'superuser/add_library_category.html', {'form': form})

# Upload Library Document
@login_required
@user_passes_test(superuser_required)
def upload_library_document(request):
    """
    Upload a document with a chosen category.
    """
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect('library_dashboard')
    else:
        form = LibraryDocumentForm()
    return render(request, 'superuser/upload_library_document.html', {'form': form})

# Download Library Document
from django.http import FileResponse

@login_required
def download_library_document(request, doc_id):
    doc = get_object_or_404(LibraryDocument, id=doc_id)
    file_path = doc.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested document was not found.")


@login_required
def audit_logs(request):
    logs = AuditLog.objects.all().order_by('-timestamp')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)

    return render(request, 'superuser/audit_logs.html', {
        'logs': logs,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def dynamic_field_filter(request):
    """
    API endpoint to filter dynamic fields based on role selection.
    """
    role = request.GET.get('role', '')
    response_data = {}

    if role == 'SECTOR_LEAD':
        response_data['sectors'] = list(Sector.objects.values('id', 'name'))
    elif role == 'EPICENTER_MANAGER':
        response_data['districts'] = list(District.objects.values('id', 'name'))
    elif role in ['ADMINISTRATIVE_USER', 'SUB_ADMIN']:
        designation_map = {
            'SUB_ADMIN': [
                'Project Manager', 'CEO', 'Director Education and Training',
                'Director Finance and Admin', 'Director Epicentre Strategy',
                'Director Cooperate Relations', 'Academic Registrar', 'Human Resource', 'Safe Guarding Officer',
            ],
            'ADMINISTRATIVE_USER': ['M&E Officer', 'MERL Coordinator', 'IT Officer'],
        }
        response_data['designations'] = designation_map.get(role, [])

    return JsonResponse(response_data)









@login_required
def dynamic_sector_filter(request):
    designation = request.GET.get('designation', '')
    sectors = Sector.objects.filter(trainer_designation=designation).values('id', 'name')
    return JsonResponse({'sectors': list(sectors)})

def dynamic_occupation_filter(request):
    sector_id = request.GET.get("sector_id")
    if sector_id:
        occupations = Occupation.objects.filter(sector_id=sector_id).values("id", "name")
        return JsonResponse({"occupations": list(occupations)})
    return JsonResponse({"occupations": []})


























































@login_required
@user_passes_test(superuser_required)
def add_trainer(request):
    """
    Add a trainer and create a corresponding user.
    """
    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            trainer_app = form.save(commit=False)
            
            # Pull out user-related fields from the form
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            designation = form.cleaned_data['designation']

            # Create the user in CustomUser
            new_user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TRAINER',             # Force trainer role
                designation=designation,    # e.g. "Artisan" or "Agribusiness Practitioner"
            )
            
            # If you want to store the created user on the TrainerApplication model,
            # add a ForeignKey to the TrainerApplication model (e.g. user = models.ForeignKey(...))
            # Then do: trainer_app.user = new_user

            trainer_app.save()
            return redirect('manage_trainers')
    else:
        form = TrainerApplicationForm()

    return render(request, 'superuser/add_trainer.html', {'form': form})

















































































# Add Trainee
@login_required
@user_passes_test(superuser_required)
def add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # We'll save the model portion
            app_obj = form.save(commit=False)

            # Pull user data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password1 = form.cleaned_data['password1']

            # Create the corresponding user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TRAINEE',
                designation='General'  # or any logic you prefer
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the application to whoever is creating it
            app_obj.created_by = request.user

            # Save the final model
            app_obj.save()

            return redirect('manage_trainees')  # or wherever
    else:
        form = TraineeApplicationForm()
    
    return render(request, 'superuser/add_trainee.html', {'form': form})



def dynamic_assigned_trainer_filter(request):
    district_id = request.GET.get("district_id")
    sector_id = request.GET.get("sector_id")
    occupation_id = request.GET.get("occupation_id")

    if district_id and sector_id and occupation_id:
        trainers = TrainerApplication.objects.filter(
            district_id=district_id,
            sector_id=sector_id,
            occupation_id=occupation_id
        ).values("id", "name")
        return JsonResponse({"trainers": list(trainers)})

    return JsonResponse({"trainers": []})


@login_required
def dynamic_epicenter_manager_filter(request):
    """
    AJAX endpoint to return epicenter managers assigned to a specific district.
    Expects ?district_id=...
    """
    district_id = request.GET.get('district_id')
    if not district_id:
        return JsonResponse({'managers': []})

    managers_qs = CustomUser.objects.filter(
        role='EPICENTER_MANAGER',
        district_id=district_id
    ).values('id', 'first_name', 'last_name', 'username')
    managers_list = []
    for m in managers_qs:
        # Combine first_name + last_name or username for display
        display_name = f"{m['first_name']} {m['last_name']}".strip()
        if not display_name:
            display_name = m['username']  # fallback
        managers_list.append({
            'id': m['id'],
            'name': display_name
        })
    return JsonResponse({'managers': managers_list})






































































































from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import UnifiedReport, ReportComment
from .forms import UnifiedReportForm, ReportCommentForm

@login_required
def forms_dashboard(request):
    approved_reports = UnifiedReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    general_approved_reports = UnifiedReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(created_by=request.user).distinct()

    pending_reports = UnifiedReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user)
    ).distinct()

    rejected_reports = UnifiedReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    context = {
        'approved_reports': approved_reports,
        'general_approved_reports': general_approved_reports,
        'pending_reports': pending_reports,
        'rejected_reports': rejected_reports,
    }
    return render(request, 'superuser/forms_dashboard.html', context)

@login_required
def submit_report(request):
    if request.method == 'POST':
        form = UnifiedReportForm(request.POST, request.FILES)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.created_by = request.user
            new_report.save()
            form.save_m2m()
            return redirect('forms_dashboard')
    else:
        form = UnifiedReportForm()
    return render(request, 'superuser/submit_report.html', {'form': form})

@login_required
def view_submitted_reports(request):
    submitted_reports = UnifiedReport.objects.filter(
        status='PENDING',
        assigned_approver=request.user
    )
    return render(request, 'superuser/view_submitted_reports.html', {'reports': submitted_reports})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(UnifiedReport, id=report_id)

    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    if request.method == 'POST':
        comment_form = ReportCommentForm(request.POST)
        if comment_form.is_valid():
            comment_obj = comment_form.save(commit=False)
            comment_obj.report = report
            comment_obj.user = request.user
            comment_obj.save()
            return redirect('report_detail', report_id=report.id)
    else:
        comment_form = ReportCommentForm()

    comments = report.comments.all().order_by('-created_at')

    return render(request, 'superuser/report_detail.html', {
        'report': report,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def report_approve(request, report_id):
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        report.status = 'APPROVED'
        report.approved_at = timezone.now().date()  # Store only date
        report.approved_by = request.user  # Track who approved the report
        report.save()
        return redirect('forms_dashboard')

    return render(request, 'superuser/approve_form.html', {'report': report})

@login_required
def report_reject(request, report_id):
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[REJECTED] {comment_text}"
            )
        report.status = 'REJECTED'
        report.save()
        return redirect('forms_dashboard')

    return render(request, 'superuser/reject_form.html', {'report': report})

@login_required
def download_report_file(request, report_id):
    report = get_object_or_404(UnifiedReport, id=report_id)

    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to download this file.")

    if not report.report_file:
        return HttpResponseNotFound("The requested report file was not found.")

    file_path = report.report_file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested report file was not found.")




@login_required
def track_report_submissions(request):
    """
    Shows all approved reports and allows filtering by start_date and end_date.
    """
    approved_reports = UnifiedReport.objects.filter(status='APPROVED').select_related('created_by')

    # Grab possible filters from GET params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter by start_date if provided
    if start_date:
        approved_reports = approved_reports.filter(created_at__gte=start_date)

    # Filter by end_date if provided
    if end_date:
        approved_reports = approved_reports.filter(created_at__lte=end_date)

    context = {
        'approved_reports': approved_reports.order_by('-created_at'),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'superuser/track_report_submissions.html', context)
























#Admin user views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import Q
from django.utils import timezone

# Import your models
from .models import (
    CustomUser, 
    TrainerApplication,
    TraineeApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment
)
# Import forms
from .forms import (
    TrainerApplicationForm,
    TraineeApplicationForm,
    LibraryCategoryForm,
    LibraryDocumentForm,
    UnifiedReportForm,
    ReportCommentForm,
)
# Import your utility function
from .utils import administrative_user_required

########################################
#  Decorator short-hands
########################################
@user_passes_test(administrative_user_required)
def admin_check(user):
    return user  # just used to keep code consistent


########################################
# 1) Administrative User Dashboard
########################################
@login_required
@user_passes_test(administrative_user_required)
def administrativeuser_dashboard(request):
    """
    Displays the list of users (subject to future updates).
    This is the 'home' for the administrative user.
    """
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'admin/dashboard.html', {
        'users': users
    })


########################################
# 2) Manage Trainers
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_manage_trainers(request):
    """
    Shows existing trainers and a button to add a trainer.
    Also a button to see "trainer enrollment" booleans.
    Functionality mirrors the superuser's manage_trainers.
    """
    trainer_users = CustomUser.objects.filter(role='TRAINER').order_by('username')
    trainer_apps = TrainerApplication.objects.all().order_by('-created_at')
    return render(request, 'admin/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
    })


@login_required
@user_passes_test(administrative_user_required)  # or use def administrative_user_required(user) ...
def admin_add_trainer(request):
    """
    Add a trainer and create a corresponding user,
    EXACTLY mirroring the superuser add_trainer logic.
    """
    # Optionally check if the user can enroll trainers:
    if not request.user.can_enroll_trainers:
        return HttpResponseForbidden("You do not have permission to enroll trainers.")

    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            trainer_app = form.save(commit=False)

            # Pull out user-related fields
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            designation = form.cleaned_data['designation']

            # Create the user in CustomUser
            new_user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TRAINER',      # Force trainer role
                designation=designation,
            )

            # Save the TrainerApplication (trainer_app.user = new_user if you added a FK)
            trainer_app.save()

            return redirect('admin_manage_trainers')
    else:
        form = TrainerApplicationForm()

    return render(request, 'admin/add_trainer.html', {'form': form})


@login_required
@user_passes_test(administrative_user_required)
def admin_trainer_enrollment_access(request):
    """
    Show all users (except trainers/trainees) with a boolean to set can_enroll_trainers.
    Mirroring the superuser's 'trainer_enrollment_access'.
    """
    users = CustomUser.objects.exclude(role__in=['TRAINER','TRAINEE']).order_by('username')

    if request.method == 'POST':
        for user in users:
            field_name = f'enrolltrainer_{user.id}'
            checked = request.POST.get(field_name)
            user.can_enroll_trainers = True if checked == 'on' else False
            user.save()
        return redirect('admin_trainer_enrollment_access')

    return render(request, 'admin/trainer_enrollment_access.html', {'users': users})


########################################
# 3) Manage Trainees
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_manage_trainees(request):
    """
    Shows existing trainees and a button to add a trainee.
    Also a button to see "trainee enrollment access".
    """
    trainee_users = CustomUser.objects.filter(role='TRAINEE').order_by('username')
    trainee_apps = TraineeApplication.objects.all().order_by('-created_at')

    return render(request, 'admin/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
    })


@login_required
@user_passes_test(administrative_user_required)
def admin_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record,
    EXACTLY mirroring the superuser add_trainee logic.
    """
    # Optionally check if the user can enroll trainees:
    if not request.user.can_enroll_trainees:
        return HttpResponseForbidden("You do not have permission to enroll trainees.")

    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Pull user data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password1 = form.cleaned_data['password1']

            # Create the corresponding user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TRAINEE',
                designation='General'  # or any logic you want
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the application to whoever is creating it
            app_obj.created_by = request.user

            # Save the final model
            app_obj.save()

            return redirect('admin_manage_trainees')
    else:
        form = TraineeApplicationForm()

    return render(request, 'admin/add_trainee.html', {'form': form})


@login_required
@user_passes_test(administrative_user_required)
def admin_trainee_enrollment_access(request):
    """
    Show all users (except trainers & trainees) with a boolean to set can_enroll_trainees.
    Mirrors superuser's 'trainee_enrollment_access'.
    """
    users = CustomUser.objects.exclude(role__in=['TRAINER','TRAINEE']).order_by('username')

    if request.method == 'POST':
        for user in users:
            field_name = f'enroll_{user.id}'
            checked = request.POST.get(field_name)
            user.can_enroll_trainees = True if checked == 'on' else False
            user.save()
        return redirect('admin_trainee_enrollment_access')

    return render(request, 'admin/trainee_enrollment_access.html', {'users': users})


########################################
# 4) Forms
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_forms_dashboard(request):
    """
    Show forms in their statuses: Pending, Approved, Rejected
    for which the admin can view or has rights to see.
    Mirrors the superuser's forms_dashboard.
    """
    # For the current user, show forms that are visible:
    approved_reports = UnifiedReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    general_approved_reports = UnifiedReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(created_by=request.user).distinct()

    pending_reports = UnifiedReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user)
    ).distinct()

    rejected_reports = UnifiedReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    context = {
        'approved_reports': approved_reports,
        'general_approved_reports': general_approved_reports,
        'pending_reports': pending_reports,
        'rejected_reports': rejected_reports,
    }
    return render(request, 'admin/forms_dashboard.html', context)


@login_required
@user_passes_test(administrative_user_required)
def admin_submit_report(request):
    """
    Create a new UnifiedReport. Identical to superuser's submit_report logic.
    """
    if request.method == 'POST':
        form = UnifiedReportForm(request.POST, request.FILES)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.created_by = request.user
            new_report.save()
            form.save_m2m()
            return redirect('admin_forms_dashboard')
    else:
        form = UnifiedReportForm()

    return render(request, 'admin/submit_report.html', {'form': form})


@login_required
@user_passes_test(administrative_user_required)
def admin_view_submitted_reports(request):
    """
    Show all PENDING reports assigned to the current user as an approver.
    """
    submitted_reports = UnifiedReport.objects.filter(
        status='PENDING',
        assigned_approver=request.user
    )
    return render(request, 'admin/view_submitted_reports.html', {'reports': submitted_reports})


@login_required
@user_passes_test(administrative_user_required)
def admin_report_detail(request, report_id):
    """
    Show a single report if the user can_view it. 
    Also handle comment submissions. Mirrors superuser's report_detail.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)

    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    if request.method == 'POST':
        comment_form = ReportCommentForm(request.POST)
        if comment_form.is_valid():
            comment_obj = comment_form.save(commit=False)
            comment_obj.report = report
            comment_obj.user = request.user
            comment_obj.save()
            return redirect('admin_report_detail', report_id=report.id)
    else:
        comment_form = ReportCommentForm()

    comments = report.comments.all().order_by('-created_at')

    return render(request, 'admin/report_detail.html', {
        'report': report,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
@user_passes_test(administrative_user_required)
def admin_report_approve(request, report_id):
    """
    Approve a Pending report if the user is the assigned_approver.
    Mirrors superuser's report_approve.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        report.status = 'APPROVED'
        report.approved_at = timezone.now().date()
        report.approved_by = request.user
        report.save()
        return redirect('admin_forms_dashboard')

    return render(request, 'admin/approve_form.html', {'report': report})


@login_required
@user_passes_test(administrative_user_required)
def admin_report_reject(request, report_id):
    """
    Reject a Pending report if the user is the assigned_approver.
    Mirrors superuser's report_reject.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[REJECTED] {comment_text}"
            )
        report.status = 'REJECTED'
        report.save()
        return redirect('admin_forms_dashboard')

    return render(request, 'admin/reject_form.html', {'report': report})


@login_required
@user_passes_test(administrative_user_required)
def admin_download_report_file(request, report_id):
    """
    Download the attached file if the user can_view the report.
    Mirrors superuser's download_report_file.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)

    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to download this file.")

    if not report.report_file:
        return HttpResponseNotFound("The requested report file was not found.")

    file_path = report.report_file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested report file was not found.")


########################################
# 5) Audit Logs
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_audit_logs(request):
    """
    Shows the Audit Logs just like the superuser, but for admin user.
    """
    logs = AuditLog.objects.all().order_by('-timestamp')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)

    return render(request, 'admin/audit_logs.html', {
        'logs': logs,
        'start_date': start_date,
        'end_date': end_date,
    })


########################################
# 6) Library
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_library_dashboard(request):
    """
    Show the library categories and documents.
    Admin can create categories and upload documents, 
    just like the superuser.
    """
    categories = LibraryCategory.objects.all().order_by('name')
    documents = LibraryDocument.objects.select_related('category').all().order_by('-created_at')
    return render(request, 'admin/library_dashboard.html', {
        'categories': categories,
        'documents': documents,
    })


@login_required
@user_passes_test(administrative_user_required)
def admin_add_library_category(request):
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_library_dashboard')
    else:
        form = LibraryCategoryForm()
    return render(request, 'admin/add_library_category.html', {'form': form})


@login_required
@user_passes_test(administrative_user_required)
def admin_upload_library_document(request):
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect('admin_library_dashboard')
    else:
        form = LibraryDocumentForm()
    return render(request, 'admin/upload_library_document.html', {'form': form})


@login_required
@user_passes_test(administrative_user_required)
def admin_download_library_document(request, doc_id):
    """
    Download the library document if it exists.
    """
    doc = get_object_or_404(LibraryDocument, id=doc_id)
    file_path = doc.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested document was not found.")


########################################
# 7) Track Report Submissions
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_track_report_submissions(request):
    """
    Shows all approved reports with optional start_date/end_date filters,
    just like the superuser's version.
    """
    approved_reports = UnifiedReport.objects.filter(status='APPROVED').select_related('created_by')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        approved_reports = approved_reports.filter(created_at__gte=start_date)
    if end_date:
        approved_reports = approved_reports.filter(created_at__lte=end_date)

    context = {
        'approved_reports': approved_reports.order_by('-created_at'),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin/track_report_submissions.html', context)























































































































#sub admin views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import Q
from django.utils import timezone

from .models import (
    CustomUser, 
    TrainerApplication,
    TraineeApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment
)
from .forms import (
    TrainerApplicationForm,
    TraineeApplicationForm,
    LibraryCategoryForm,
    LibraryDocumentForm,
    UnifiedReportForm,
    ReportCommentForm,
)
########################################
# 1) SUB_ADMIN Dashboard
########################################
@login_required
@user_passes_test(sub_admin_required)
def subadmin_dashboard(request):
    """
    Displays a list of users or any relevant SUB_ADMIN info.
    """
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'subadmin/dashboard.html', {
        'users': users,
    })


########################################
# 2) Manage Trainers
########################################
@login_required
@user_passes_test(sub_admin_required)
def subadmin_manage_trainers(request):
    """
    Shows existing trainers, a button to add a trainer if
    this SUB_ADMIN can_enroll_trainers == True.
    """
    trainer_users = CustomUser.objects.filter(role='TRAINER').order_by('username')
    trainer_apps = TrainerApplication.objects.all().order_by('-created_at')
    return render(request, 'subadmin/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
    })


@login_required
@user_passes_test(sub_admin_required)
def subadmin_add_trainer(request):
    """
    Add a trainer and create a corresponding user,
    EXACTLY mirroring the superuser add_trainer logic.
    """
    # Optionally check if the user can enroll trainers:
    if not request.user.can_enroll_trainers:
        return HttpResponseForbidden("You do not have permission to enroll trainers.")

    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            trainer_app = form.save(commit=False)

            # Pull out user-related fields
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            designation = form.cleaned_data['designation']

            # Create the user
            new_user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TRAINER',
                designation=designation,
            )

            # Save the TrainerApplication 
            trainer_app.save()

            return redirect('subadmin_manage_trainers')
    else:
        form = TrainerApplicationForm()

    return render(request, 'subadmin/add_trainer.html', {'form': form})


########################################
# 3) Manage Trainees
########################################
@login_required
@user_passes_test(sub_admin_required)
def subadmin_manage_trainees(request):
    """
    Shows existing trainees, a button to add a trainee if
    subadmin has can_enroll_trainees == True.
    """
    trainee_users = CustomUser.objects.filter(role='TRAINEE').order_by('username')
    trainee_apps = TraineeApplication.objects.all().order_by('-created_at')
    return render(request, 'subadmin/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
    })

@login_required
@user_passes_test(sub_admin_required)
def subadmin_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record,
    EXACTLY mirroring the superuser add_trainee logic.
    """
    # Optionally check if the user can enroll trainees:
    if not request.user.can_enroll_trainees:
        return HttpResponseForbidden("You do not have permission to enroll trainees.")

    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Pull user data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password1 = form.cleaned_data['password1']

            # Create the corresponding user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the application
            app_obj.created_by = request.user
            app_obj.save()

            return redirect('subadmin_manage_trainees')
    else:
        form = TraineeApplicationForm()

    return render(request, 'subadmin/add_trainee.html', {'form': form})


########################################
# 4) Forms
########################################
@login_required
@user_passes_test(sub_admin_required)
def subadmin_forms_dashboard(request):
    """
    Show forms in their statuses: Pending, Approved, Rejected
    for which this SUB_ADMIN can view or has rights (as creator or approver).
    """
    approved_reports = UnifiedReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    general_approved_reports = UnifiedReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(created_by=request.user).distinct()

    pending_reports = UnifiedReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user)
    ).distinct()

    rejected_reports = UnifiedReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    context = {
        'approved_reports': approved_reports,
        'general_approved_reports': general_approved_reports,
        'pending_reports': pending_reports,
        'rejected_reports': rejected_reports,
    }
    return render(request, 'subadmin/forms_dashboard.html', context)


@login_required
@user_passes_test(sub_admin_required)
def subadmin_submit_report(request):
    """
    Create a new UnifiedReport, assigned_approver can be any user
    that isn't trainer/trainee, etc. 
    """
    if request.method == 'POST':
        form = UnifiedReportForm(request.POST, request.FILES)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.created_by = request.user
            new_report.save()
            form.save_m2m()
            return redirect('subadmin_forms_dashboard')
    else:
        form = UnifiedReportForm()

    return render(request, 'subadmin/submit_report.html', {'form': form})


@login_required
@user_passes_test(sub_admin_required)
def subadmin_view_submitted_reports(request):
    """
    Show all PENDING reports assigned to the current sub-admin for approval.
    """
    submitted_reports = UnifiedReport.objects.filter(
        status='PENDING',
        assigned_approver=request.user
    )
    return render(request, 'subadmin/view_submitted_reports.html', {'reports': submitted_reports})


@login_required
@user_passes_test(sub_admin_required)
def subadmin_report_detail(request, report_id):
    """
    Show a single report if subadmin can view it.
    Also handle comment submission.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)

    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    if request.method == 'POST':
        comment_form = ReportCommentForm(request.POST)
        if comment_form.is_valid():
            comment_obj = comment_form.save(commit=False)
            comment_obj.report = report
            comment_obj.user = request.user
            comment_obj.save()
            return redirect('subadmin_report_detail', report_id=report.id)
    else:
        comment_form = ReportCommentForm()

    comments = report.comments.all().order_by('-created_at')

    return render(request, 'subadmin/report_detail.html', {
        'report': report,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
@user_passes_test(sub_admin_required)
def subadmin_report_approve(request, report_id):
    """
    Approve a Pending report if the user is the assigned_approver.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        report.status = 'APPROVED'
        report.approved_at = timezone.now().date()
        report.approved_by = request.user
        report.save()
        return redirect('subadmin_forms_dashboard')

    return render(request, 'subadmin/approve_form.html', {'report': report})


@login_required
@user_passes_test(sub_admin_required)
def subadmin_report_reject(request, report_id):
    """
    Reject a Pending report if the user is the assigned_approver.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[REJECTED] {comment_text}"
            )
        report.status = 'REJECTED'
        report.save()
        return redirect('subadmin_forms_dashboard')

    return render(request, 'subadmin/reject_form.html', {'report': report})


@login_required
@user_passes_test(sub_admin_required)
def subadmin_download_report_file(request, report_id):
    """
    Download the attached file if the user can_view the report.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to download this file.")
    if not report.report_file:
        return HttpResponseNotFound("The requested report file was not found.")

    file_path = report.report_file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested report file was not found.")


########################################
# 5) Audit Logs
########################################
@login_required
@user_passes_test(sub_admin_required)
def subadmin_audit_logs(request):
    """
    Shows the Audit Logs, same as admin but for SUB_ADMIN usage.
    """
    logs = AuditLog.objects.all().order_by('-timestamp')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)

    return render(request, 'subadmin/audit_logs.html', {
        'logs': logs,
        'start_date': start_date,
        'end_date': end_date,
    })


########################################
# 6) Library
########################################
@login_required
@user_passes_test(sub_admin_required)
def subadmin_library_dashboard(request):
    """
    Show the library categories and documents.
    """
    categories = LibraryCategory.objects.all().order_by('name')
    documents = LibraryDocument.objects.select_related('category').all().order_by('-created_at')
    return render(request, 'subadmin/library_dashboard.html', {
        'categories': categories,
        'documents': documents,
    })


@login_required
@user_passes_test(sub_admin_required)
def subadmin_add_library_category(request):
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subadmin_library_dashboard')
    else:
        form = LibraryCategoryForm()
    return render(request, 'subadmin/add_library_category.html', {'form': form})


@login_required
@user_passes_test(sub_admin_required)
def subadmin_upload_library_document(request):
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect('subadmin_library_dashboard')
    else:
        form = LibraryDocumentForm()
    return render(request, 'subadmin/upload_library_document.html', {'form': form})


@login_required
@user_passes_test(sub_admin_required)
def subadmin_download_library_document(request, doc_id):
    doc = get_object_or_404(LibraryDocument, id=doc_id)
    file_path = doc.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested document was not found.")




























































































# epicenter manager views

# epicentermanager_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import Q
from django.utils import timezone

from .models import (
    CustomUser,
    TrainerApplication,
    TraineeApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment,
    District
)
from .forms import (
    TrainerApplicationForm,
    TraineeApplicationForm,
    LibraryCategoryForm,
    LibraryDocumentForm,
    UnifiedReportForm,
    ReportCommentForm,
)
from .utils import epicenter_manager_required

#
# OPTIONAL:
# If you want specialized "profile update" forms for trainers & trainees,
# create them. (See section 3.2 below.)
#

########################################
# Decorator usage
########################################
@user_passes_test(epicenter_manager_required)
def epicenter_manager_check(user):
    return user  # pass-through to maintain code consistency


########################################
# 1) Dashboard
########################################
@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_manager_dashboard(request):
    """
    Shows a simple list of all users. (Subject to change in future.)
    """
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'epicentermanager/dashboard.html', {
        'users': users,
    })


########################################
# 2) Trainers
########################################
@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_manage_trainers(request):
    """
    Shows only trainers in the *epicenter manager's district*.
    Also a button to add trainer (if can_enroll_trainers).
    """
    manager_district = request.user.district
    trainer_users = CustomUser.objects.filter(
        role='TRAINER',
        district=manager_district
    ).order_by('username')
    trainer_apps = TrainerApplication.objects.filter(district=manager_district).order_by('-created_at')

    return render(request, 'epicentermanager/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'manager_district': manager_district,
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_add_trainer(request):
    if not request.user.can_enroll_trainers:
        return HttpResponseForbidden("You do not have permission to enroll trainers.")

    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            trainer_app = form.save(commit=False)
            trainer_app.district = request.user.district  # Force district assignment
            
            # Create the user associated with the trainer
            new_user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='TRAINER',
                designation=form.cleaned_data['designation'],
            )

            # Link the trainer application to the created user
            trainer_app.user = new_user
            trainer_app.save()
            return redirect('epicenter_manage_trainers')
    else:
        form = TrainerApplicationForm(request=request)

    return render(request, 'epicentermanager/add_trainer.html', {'form': form})



########################################
# 3) Trainees
########################################
@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_manage_trainees(request):
    """
    Shows only trainees in the epicenter manager's district.
    Also a button to add trainee (if can_enroll_trainees).
    """
    manager_district = request.user.district
    trainee_users = CustomUser.objects.filter(
        role='TRAINEE',
        district=manager_district
    ).order_by('username')
    trainee_apps = TraineeApplication.objects.filter(district=manager_district).order_by('-created_at')

    return render(request, 'epicentermanager/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'manager_district': manager_district,
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_add_trainee(request):
    if not request.user.can_enroll_trainees:
        return HttpResponseForbidden("You do not have permission to enroll trainees.")

    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            trainee_app = form.save(commit=False)
            trainee_app.district = request.user.district  # Force district assignment

            # Create the user associated with the trainee
            new_user = CustomUser.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(form.cleaned_data['password1'])
            new_user.save()

            # Link the trainee application to the created user
            trainee_app.user = new_user
            trainee_app.save()
            return redirect('epicenter_manage_trainees')
    else:
        form = TraineeApplicationForm(request=request)

    return render(request, 'epicentermanager/add_trainee.html', {'form': form})


########################################
# 4) Track Trainees & Trainers
########################################
#
# The epicenter manager can update certain fields for trainees and trainers:
# - Trainees: phone number, monthly income, current_location
# - Trainers: phone_contact, monthly_income (Dropdown?), location, education_level
#
# We'll implement separate views for listing, then an edit form.

from .forms import TraineeProfileUpdateForm, TrainerProfileUpdateForm

@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_track_home(request):
    """
    A simple page that offers links to:
    - Track Trainees
    - Track Trainers
    """
    return render(request, 'epicentermanager/track_home.html')


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_track_trainees(request):
    """
    Show all trainees in this manager's district, each with an 'Edit' link.
    """
    manager_district = request.user.district
    trainees = TraineeApplication.objects.filter(district=manager_district)
    return render(request, 'epicentermanager/track_trainees.html', {
        'trainees': trainees
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_edit_trainee(request, trainee_id):
    """
    Edit phone number, monthly income, current_location for a single trainee in manager's district.
    """
    manager_district = request.user.district
    trainee_obj = get_object_or_404(TraineeApplication, id=trainee_id, district=manager_district)

    if request.method == 'POST':
        form = TraineeProfileUpdateForm(request.POST, instance=trainee_obj)
        if form.is_valid():
            form.save()
            return redirect('epicenter_track_trainees')
    else:
        form = TraineeProfileUpdateForm(instance=trainee_obj)

    return render(request, 'epicentermanager/edit_trainee.html', {
        'form': form,
        'trainee': trainee_obj
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_track_trainers(request):
    """
    Show all trainers in this manager's district, each with an 'Edit' link.
    """
    manager_district = request.user.district
    trainers = TrainerApplication.objects.filter(district=manager_district)
    return render(request, 'epicentermanager/track_trainers.html', {
        'trainers': trainers
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_edit_trainer(request, trainer_id):
    """
    Edit phone_contact, monthly_income, location, education_level for a single trainer in manager's district.
    """
    manager_district = request.user.district
    trainer_obj = get_object_or_404(TrainerApplication, id=trainer_id, district=manager_district)

    if request.method == 'POST':
        form = TrainerProfileUpdateForm(request.POST, instance=trainer_obj)
        if form.is_valid():
            form.save()
            return redirect('epicenter_track_trainers')
    else:
        form = TrainerProfileUpdateForm(instance=trainer_obj)

    return render(request, 'epicentermanager/edit_trainer.html', {
        'form': form,
        'trainer': trainer_obj
    })


########################################
# 5) Forms
########################################
@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_forms_dashboard(request):
    """
    Identical to admin forms dashboard:
      - show PENDING, APPROVED, REJECTED, etc.
    """
    approved_reports = UnifiedReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    general_approved_reports = UnifiedReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(created_by=request.user).distinct()

    pending_reports = UnifiedReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user)
    ).distinct()

    rejected_reports = UnifiedReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    context = {
        'approved_reports': approved_reports,
        'general_approved_reports': general_approved_reports,
        'pending_reports': pending_reports,
        'rejected_reports': rejected_reports,
    }
    return render(request, 'epicentermanager/forms_dashboard.html', context)


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_submit_report(request):
    """
    Create a new UnifiedReport, identical logic to admin_submi_report.
    """
    if request.method == 'POST':
        form = UnifiedReportForm(request.POST, request.FILES)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.created_by = request.user
            new_report.save()
            form.save_m2m()
            return redirect('epicenter_forms_dashboard')
    else:
        form = UnifiedReportForm()

    return render(request, 'epicentermanager/submit_report.html', {'form': form})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_view_submitted_reports(request):
    """
    Show all PENDING reports assigned to the epicenter manager for approval.
    """
    submitted_reports = UnifiedReport.objects.filter(
        status='PENDING',
        assigned_approver=request.user
    )
    return render(request, 'epicentermanager/view_submitted_reports.html', {'reports': submitted_reports})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_report_detail(request, report_id):
    """
    Show a single report if the user can_view it + handle comment submissions.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    if request.method == 'POST':
        comment_form = ReportCommentForm(request.POST)
        if comment_form.is_valid():
            comment_obj = comment_form.save(commit=False)
            comment_obj.report = report
            comment_obj.user = request.user
            comment_obj.save()
            return redirect('epicenter_report_detail', report_id=report.id)
    else:
        comment_form = ReportCommentForm()

    comments = report.comments.all().order_by('-created_at')
    return render(request, 'epicentermanager/report_detail.html', {
        'report': report,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_report_approve(request, report_id):
    """
    Approve a pending report if assigned_approver == request.user.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        report.status = 'APPROVED'
        report.approved_at = timezone.now().date()
        report.approved_by = request.user
        report.save()
        return redirect('epicenter_forms_dashboard')

    return render(request, 'epicentermanager/approve_form.html', {'report': report})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_report_reject(request, report_id):
    """
    Reject a pending report if assigned_approver == request.user.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[REJECTED] {comment_text}"
            )
        report.status = 'REJECTED'
        report.save()
        return redirect('epicenter_forms_dashboard')

    return render(request, 'epicentermanager/reject_form.html', {'report': report})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_download_report_file(request, report_id):
    """
    Download the file if the user can_view the report.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to download this file.")

    if not report.report_file:
        return HttpResponseNotFound("The requested report file was not found.")

    file_path = report.report_file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested report file was not found.")


########################################
# 6) Library
########################################
@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_library_dashboard(request):
    """
    Identical to admin library dashboard:
      - show categories
      - show documents
      - can upload, etc.
    """
    categories = LibraryCategory.objects.all().order_by('name')
    documents = LibraryDocument.objects.select_related('category').all().order_by('-created_at')
    return render(request, 'epicentermanager/library_dashboard.html', {
        'categories': categories,
        'documents': documents,
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_add_library_category(request):
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('epicenter_library_dashboard')
    else:
        form = LibraryCategoryForm()
    return render(request, 'epicentermanager/add_library_category.html', {'form': form})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_upload_library_document(request):
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect('epicenter_library_dashboard')
    else:
        form = LibraryDocumentForm()
    return render(request, 'epicentermanager/upload_library_document.html', {'form': form})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_download_library_document(request, doc_id):
    doc = get_object_or_404(LibraryDocument, id=doc_id)
    file_path = doc.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested document was not found.")
    





































































































































































































# sectorlead_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import Q
from django.utils import timezone

from .models import (
    CustomUser,
    TrainerApplication,
    TraineeApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment,
    Sector
)
from .forms import (
    TrainerApplicationForm,
    TraineeApplicationForm,
    LibraryCategoryForm,
    LibraryDocumentForm,
    UnifiedReportForm,
    ReportCommentForm
)



########################################
# 1) Dashboard
########################################
@login_required
@user_passes_test(sector_lead_required)
def sector_lead_dashboard(request):
    """
    Displays the list of users (subject to future changes).
    This is the 'home' for the sector lead.
    """
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'sectorlead/dashboard.html', {'users': users})


########################################
# 2) Manage Trainers
########################################
@login_required
@user_passes_test(sector_lead_required)
def sector_lead_manage_trainers(request):
    """
    Shows trainers that belong to the sector lead's assigned sector.
    Also a button to add trainer if can_enroll_trainers.
    """
    # The Sector Lead is assigned to request.user.sector
    lead_sector = request.user.sector

    # Filter trainers by sector
    # The CustomUser might store the sector if we set it when creating a trainer user,
    # but more reliably we can filter by the TrainerApplication itself.
    # We'll do both to show you the pattern:
    trainer_users = CustomUser.objects.filter(role='TRAINER', sector=lead_sector)
    trainer_apps = TrainerApplication.objects.filter(sector=lead_sector).order_by('-created_at')

    return render(request, 'sectorlead/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'lead_sector': lead_sector,
    })


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_add_trainer(request):
    """
    Creates a new Trainer (and user) within the sector lead's assigned sector,
    similarly to Admin/Sub-Admin. 
    """
    if not request.user.can_enroll_trainers:
        return HttpResponseForbidden("You do not have permission to enroll trainers.")

    if request.method == 'POST':
        # Pass request so we can fix the sector in the form
        form = TrainerApplicationForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            trainer_app = form.save(commit=False)

            # Force the trainer's sector = sector lead's sector
            lead_sector = request.user.sector
            trainer_app.sector = lead_sector

            # Create corresponding user
            new_user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='TRAINER',
                designation=form.cleaned_data['designation'],
                sector=lead_sector  # Force the sector on the user record too
            )
            # Link the trainer_app to that user if you have a foreign key in your model
            # E.g. trainer_app.user = new_user
            trainer_app.save()
            return redirect('sector_lead_manage_trainers')
    else:
        form = TrainerApplicationForm(request=request)

    return render(request, 'sectorlead/add_trainer.html', {'form': form})


########################################
# 3) Manage Trainees
########################################
@login_required
@user_passes_test(sector_lead_required)
def sector_lead_manage_trainees(request):
    """
    Shows only trainees within the sector lead's assigned sector.
    Also a button to add a trainee (if can_enroll_trainees).
    """
    lead_sector = request.user.sector
    # Filter CustomUser with role=TRAINEE if you store sector on the user
    # or filter by TraineeApplication if you rely on the model there
    trainee_users = CustomUser.objects.filter(role='TRAINEE', sector=lead_sector)
    # TraineeApplication stores sector in the sector field
    trainee_apps = TraineeApplication.objects.filter(sector=lead_sector).order_by('-created_at')

    return render(request, 'sectorlead/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'lead_sector': lead_sector,
    })


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_add_trainee(request):
    """
    Creates a new user (role=TRAINEE) + TraineeApplication, forced to the sector lead's sector.
    """
    if not request.user.can_enroll_trainees:
        return HttpResponseForbidden("You do not have permission to enroll trainees.")

    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            trainee_app = form.save(commit=False)
            lead_sector = request.user.sector
            trainee_app.sector = lead_sector  # Force the sector in the application

            # Create the user
            new_user = CustomUser.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='TRAINEE',
                designation='General',
                sector=lead_sector  # Force the sector on the user record
            )
            new_user.set_password(form.cleaned_data['password1'])
            new_user.save()

            # Link the app to whoever is creating it
            trainee_app.created_by = request.user

            # Save the final model
            trainee_app.save()
            return redirect('sector_lead_manage_trainees')
    else:
        form = TraineeApplicationForm(request=request)

    return render(request, 'sectorlead/add_trainee.html', {'form': form})


########################################
# 4) Forms
########################################
@login_required
@user_passes_test(sector_lead_required)
def sector_lead_forms_dashboard(request):
    """
    Show forms in statuses: Pending, Approved, Rejected
    for which this Sector Lead can view or has rights to see.
    Mirrors admin/subadmin forms_dashboard.
    """
    approved_reports = UnifiedReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    general_approved_reports = UnifiedReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(created_by=request.user).distinct()

    pending_reports = UnifiedReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user)
    ).distinct()

    rejected_reports = UnifiedReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(created_by=request.user) | Q(assigned_approver=request.user) | Q(viewers=request.user)
    ).distinct()

    context = {
        'approved_reports': approved_reports,
        'general_approved_reports': general_approved_reports,
        'pending_reports': pending_reports,
        'rejected_reports': rejected_reports,
    }
    return render(request, 'sectorlead/forms_dashboard.html', context)


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_submit_report(request):
    """
    Submit a new UnifiedReport (same approach as admin/subadmin).
    """
    if request.method == 'POST':
        form = UnifiedReportForm(request.POST, request.FILES)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.created_by = request.user
            new_report.save()
            form.save_m2m()
            return redirect('sector_lead_forms_dashboard')
    else:
        form = UnifiedReportForm()

    return render(request, 'sectorlead/submit_report.html', {'form': form})


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_view_submitted_reports(request):
    """
    Show all PENDING reports assigned to this sector lead for approval.
    """
    submitted_reports = UnifiedReport.objects.filter(
        status='PENDING',
        assigned_approver=request.user
    )
    return render(request, 'sectorlead/view_submitted_reports.html', {'reports': submitted_reports})


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_report_detail(request, report_id):
    """
    Show single report if sector lead can view it. Handle comment submission.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    if request.method == 'POST':
        comment_form = ReportCommentForm(request.POST)
        if comment_form.is_valid():
            comment_obj = comment_form.save(commit=False)
            comment_obj.report = report
            comment_obj.user = request.user
            comment_obj.save()
            return redirect('sector_lead_report_detail', report_id=report.id)
    else:
        comment_form = ReportCommentForm()

    comments = report.comments.all().order_by('-created_at')
    return render(request, 'sectorlead/report_detail.html', {
        'report': report,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_report_approve(request, report_id):
    """
    Approve a pending report if assigned_approver == request.user.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        report.status = 'APPROVED'
        report.approved_at = timezone.now().date()
        report.approved_by = request.user
        report.save()
        return redirect('sector_lead_forms_dashboard')

    return render(request, 'sectorlead/approve_form.html', {'report': report})


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_report_reject(request, report_id):
    """
    Reject a pending report if assigned_approver == request.user.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if report.assigned_approver != request.user:
        return HttpResponseForbidden("You are not the approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                comment=f"[REJECTED] {comment_text}"
            )
        report.status = 'REJECTED'
        report.save()
        return redirect('sector_lead_forms_dashboard')

    return render(request, 'sectorlead/reject_form.html', {'report': report})


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_download_report_file(request, report_id):
    """
    Download the attached file if the user can_view the report.
    """
    report = get_object_or_404(UnifiedReport, id=report_id)
    if not report.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to download this file.")

    if not report.report_file:
        return HttpResponseNotFound("The requested report file was not found.")

    file_path = report.report_file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested report file was not found.")


########################################
# 5) Library
########################################
@login_required
@user_passes_test(sector_lead_required)
def sector_lead_library_dashboard(request):
    """
    Show library categories & docs. The sector lead can create categories,
    upload docs, etc., exactly like admin/subadmin.
    """
    categories = LibraryCategory.objects.all().order_by('name')
    documents = LibraryDocument.objects.select_related('category').all().order_by('-created_at')
    return render(request, 'sectorlead/library_dashboard.html', {
        'categories': categories,
        'documents': documents,
    })


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_add_library_category(request):
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sector_lead_library_dashboard')
    else:
        form = LibraryCategoryForm()
    return render(request, 'sectorlead/add_library_category.html', {'form': form})


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_upload_library_document(request):
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect('sector_lead_library_dashboard')
    else:
        form = LibraryDocumentForm()
    return render(request, 'sectorlead/upload_library_document.html', {'form': form})


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_download_library_document(request, doc_id):
    doc = get_object_or_404(LibraryDocument, id=doc_id)
    file_path = doc.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested document was not found.")

