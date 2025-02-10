from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from .utils import administrative_user_required, superuser_required, sub_admin_required, epicenter_manager_required,sector_lead_required,trainer_required,trainee_required, trainee_required,data_entrant_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
import json
from itertools import chain
from django.db.models import Value, CharField
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.conf import settings
import csv

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
    LibraryDocument,
    TrainingModule,

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
    EnrollmentAccessForm,
    TrainingModuleForm,
    ManagerTraineeStatusForm,
    RegistrarAssessmentForm,
    CohortForm,
    OccupationeForm,
    TraineeApplicationEditForm,
    TrainerApplicationEditForm,


)


# Login View
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == "SUPER_USER":
            return redirect("superuser_dashboard")
        elif request.user.role == "DATA_ENTRANT":
            return redirect("de_dashboard")
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
            elif request.user.role == "DATA_ENTRANT":
                return redirect("de_dashboard")
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
    # 1) Grab ALL cohorts for the dropdown
    all_cohorts = Cohort.objects.all().order_by('name')
    selected_cohort_id = request.GET.get('cohort', 'all')

    # 2) Build the base queryset
    trainees_qs = TraineeApplication.objects.all()
    if selected_cohort_id != 'all':
        # Validate cohort_id
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass  # handle error if needed

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()  # Total "Completed"

    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA ================
    # Per the instructions, this should be the sum of Total Employed + Total Self-Employed (both completed)
    total_in_work = total_self_employed + total_employed

    # For the chart breakdown by sector (female first, then male),
    # we consider only those who are COMPLETED & employed/self-employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # All sectors
    all_sectors = Sector.objects.all().order_by('name')
    sector_gender_list = []
    for sector in all_sectors:
        # Female first, then male
        female_count = in_work_qs.filter(sector=sector, gender="Female").count()
        male_count = in_work_qs.filter(sector=sector, gender="Male").count()
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Female",
            "count": female_count
        })
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Male",
            "count": male_count
        })
    sector_gender_json = json.dumps(sector_gender_list)

    # ================ OUTREACH DATA ================
    # Outreach = all individuals enrolled (any study status in the cohort)
    total_outreach = trainees_qs.count()

    # For the outreach chart by district (female first, then male),
    # we consider ALL individuals in trainees_qs
    all_districts = District.objects.all().order_by('name')
    district_gender_list = []
    for dist in all_districts:
        female_count = trainees_qs.filter(district=dist, gender="Female").count()
        male_count = trainees_qs.filter(district=dist, gender="Male").count()
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Female",
            "count": female_count
        })
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Male",
            "count": male_count
        })
    district_gender_json = json.dumps(district_gender_list)

    # ================ ASSESSMENT DATA ================
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_sector_list = []
    for sector in all_sectors:
        successful_count = successful_assessed_qs.filter(sector=sector).count()
        successful_sector_list.append({
            "sector__name": sector.name,
            "count": successful_count
        })
    successful_sector_json = json.dumps(successful_sector_list)

    context = {
        # For the dropdown
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,

        # Banners (all referencing COMPLETED trainees)
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work
        "total_in_work": total_in_work,
        "sector_gender_data": sector_gender_json,

        # Outreach
        "total_outreach": total_outreach,
        "district_gender_data": district_gender_json,

        # Assessment
        "successful_sector_data": successful_sector_json,
    }

    return render(request, "superuser/dashboard.html", context)


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

@login_required
@user_passes_test(superuser_required)
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("manage_users")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "superuser/update_user.html", {"form": form, "user_obj": user})

@login_required
@user_passes_test(superuser_required)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect("manage_users")


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

@login_required
@user_passes_test(superuser_required)
def edit_phase(request, phase_id):
    """
    Edit an existing phase.
    """
    phase = get_object_or_404(Phase, id=phase_id)

    if request.method == "POST":
        form = PhaseForm(request.POST, instance=phase)
        if form.is_valid():
            form.save()
            return redirect("manage_phases")
    else:
        form = PhaseForm(instance=phase)

    return render(request, "superuser/edit_phase.html", {"form": form, "phase": phase})

@login_required
@user_passes_test(superuser_required)
def delete_phase(request, phase_id):
    """
    Delete a phase.
    """
    phase = get_object_or_404(Phase, id=phase_id)
    phase.delete()
    return redirect("manage_phases")

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

@login_required
@user_passes_test(superuser_required)
def edit_cohort(request, cohort_id):
    """
    Edit an existing cohort.
    """
    cohort = get_object_or_404(Cohort, id=cohort_id)

    if request.method == "POST":
        form = CohortForm(request.POST, instance=cohort)
        if form.is_valid():
            form.save()
            return redirect("manage_phases")
    else:
        form = CohortForm(instance=cohort)

    return render(request, "superuser/edit_cohort.html", {"form": form, "cohort": cohort})

@login_required
@user_passes_test(superuser_required)
def delete_cohort(request, cohort_id):
    """
    Delete a cohort.
    """
    cohort = get_object_or_404(Cohort, id=cohort_id)
    cohort.delete()
    return redirect("manage_phases")


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

# Edit Sector
@login_required
@user_passes_test(superuser_required)
def edit_sector(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    if request.method == 'POST':
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            form.save()
            return redirect('manage_sectors')
    else:
        form = SectorForm(instance=sector)
    return render(request, 'superuser/edit_sector.html', {'form': form, 'sector': sector})

# Delete Sector
@login_required
@user_passes_test(superuser_required)
def delete_sector(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    if request.method == 'POST':
        sector.delete()
        return redirect('manage_sectors')
    return render(request, 'superuser/delete_sector.html', {'sector': sector})

# Edit Occupation
@login_required
@user_passes_test(superuser_required)
def edit_occupation(request, occupation_id):
    occupation = get_object_or_404(Occupation, id=occupation_id)
    if request.method == 'POST':
        form = OccupationeForm(request.POST, instance=occupation)
        if form.is_valid():
            form.save()
            return redirect('manage_sectors')
    else:
        form = OccupationeForm(instance=occupation)
    return render(request, 'superuser/edit_occupation.html', {'form': form, 'occupation': occupation})

# Delete Occupation
@login_required
@user_passes_test(superuser_required)
def delete_occupation(request, occupation_id):
    occupation = get_object_or_404(Occupation, id=occupation_id)
    if request.method == 'POST':
        occupation.delete()
        return redirect('manage_sectors')
    return render(request, 'superuser/delete_occupation.html', {'occupation': occupation})


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

# Edit District
@login_required
@user_passes_test(superuser_required)
def edit_district(request, district_id):
    district = get_object_or_404(District, id=district_id)
    if request.method == 'POST':
        form = DistrictForm(request.POST, instance=district)
        if form.is_valid():
            form.save()
            return redirect('manage_districts')
    else:
        form = DistrictForm(instance=district)
    return render(request, 'superuser/edit_district.html', {'form': form, 'district': district})

# Delete District
@login_required
@user_passes_test(superuser_required)
def delete_district(request, district_id):
    district = get_object_or_404(District, id=district_id)
    if request.method == "POST":
        district.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})


#manage trainees
@login_required
@user_passes_test(superuser_required)
def manage_trainees(request):
    """
    Show existing trainees with search functionality by name.
    """
    trainee_users = CustomUser.objects.filter(role='TRAINEE').order_by('username')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainee_apps = TraineeApplication.objects.filter(
            applicant_name__icontains=search_query  # Case-insensitive search
        ).order_by('-created_at')
    else:
        trainee_apps = TraineeApplication.objects.all().order_by('-created_at')

    context = {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'search_query': search_query,
    }
    return render(request, 'superuser/manage_trainees.html', context)





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

@login_required
@user_passes_test(superuser_required)
def view_trainee(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    form = TraineeApplicationEditForm(instance=trainee)
    # Disable fields in the view if you like:
    for f in form.fields:
        form.fields[f].disabled = True

    return render(request, 'superuser/single_trainee_form.html', {
        'form': form,
        'heading': 'View Trainee (Read-Only)',
        'read_only': True,
    })


@login_required
@user_passes_test(superuser_required)
def edit_trainee(request, trainee_id):
    if not request.user.can_enroll_trainees:
        return render(
            request,
            'superuser/no_permission.html',
            {"message": "You do not have permission to edit trainees."}
        )

    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, instance=trainee, request=request)
        if form.is_valid():
            trainee = form.save(commit=False)
            if trainee.created_by:
                user = trainee.created_by
                new_username = form.cleaned_data.get("username")
                new_email = form.cleaned_data.get("email")
                new_password = form.cleaned_data.get("password1")
                
                if new_username:
                    user.username = new_username
                if new_email:
                    user.email = new_email
                if new_password:
                    user.set_password(new_password)
                user.save()
            trainee.save()
            return redirect('manage_trainees')
    else:
        form = TraineeApplicationForm(instance=trainee, request=request)
    return render(request, 'superuser/edit_trainee.html', {
        'form': form,
        'heading': 'Edit Trainee',
        'read_only': False,
    })




@login_required
@user_passes_test(superuser_required)
def delete_trainee(request, trainee_id):
    """
    Deletes a TraineeApplication AND its associated CustomUser.
    """
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)

    if trainee.created_by:
        trainee.created_by.delete()
    else:
        trainee.delete()

    return redirect('manage_trainees')

#manage trainers
@login_required
@user_passes_test(superuser_required)
def manage_trainers(request):
    """
    Show existing trainers and buttons for adding a trainer or viewing trainer enrollment access.
    Includes case‑insensitive search functionality by trainer name.
    """
    trainer_users = CustomUser.objects.filter(role='TRAINER').order_by('username')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainer_apps = TrainerApplication.objects.filter(
            name__icontains=search_query  # Case-insensitive search on trainer name
        ).order_by('-created_at')
    else:
        trainer_apps = TrainerApplication.objects.all().order_by('-created_at')

    context = {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'search_query': search_query,
    }
    return render(request, 'superuser/manage_trainers.html', context)







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









@login_required
@user_passes_test(superuser_required)
def library_dashboard(request):
    """
    Library page: show docs by category, and allow 
    superuser to create categories and upload documents with pagination.
    """
    categories = LibraryCategory.objects.all().order_by('name')
    documents_list = LibraryDocument.objects.select_related('category').all().order_by('-created_at')

    # Implement Pagination (10 items per page)
    paginator = Paginator(documents_list, 10)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)

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

    # Paginate logs (30 per page)
    paginator = Paginator(logs, 15)
    page_number = request.GET.get('page')
    page_logs = paginator.get_page(page_number)

    return render(request, 'superuser/audit_logs.html', {
        'logs': page_logs,  # Paginated logs
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
    elif role == 'DATA_ENTRANT':
        response_data['districts'] = list(District.objects.values('id', 'name'))
    elif role in ['ADMINISTRATIVE_USER', 'SUB_ADMIN']:
        designation_map = {
            'SUB_ADMIN': [
                'Project Manager', 'CEO', 'Director Education and Training',
                'Director Finance and Admin', 'Director Epicentre Strategy',
                'Director Cooperate Relations', 'Academic Registrar', 'Human Resource', 'Safe Guarding Officer','Principal','Accountant'
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
            designation = form.cleaned_data['designation']

            # Create the user in CustomUser
            new_user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                email=email,
                role='TRAINER',             # Force trainer role
                designation=designation,    # e.g. "Artisan" or "Agribusiness Practitioner"
            )
            
            # Link the trainer application to the newly created user
            trainer_app.user = new_user  # THIS IS THE MISSING LINE
            trainer_app.save()

            return redirect('manage_trainers')
    else:
        form = TrainerApplicationForm()

    return render(request, 'superuser/add_trainer.html', {'form': form})











@login_required
@user_passes_test(superuser_required)
def view_trainer(request, trainer_id):
    """
    Display a read-only view of a TrainerApplication.
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    form = TrainerApplicationEditForm(instance=trainer)
    # Disable all fields for read-only
    for field in form.fields:
        form.fields[field].disabled = True
    return render(request, 'superuser/single_trainer_form.html', {
        'form': form,
        'heading': 'View Trainer (Read-Only)',
        'read_only': True,
    })

@login_required
@user_passes_test(superuser_required)
def edit_trainer(request, trainer_id):
    """
    Allow editing a TrainerApplication only if the current user has can_enroll_trainers enabled.
    Also update the associated user’s username, email, password, and designation.
    """
    if not request.user.can_enroll_trainers:
        return render(request, 'superuser/no_permission2.html', {
            'message': "You do not have permission to edit trainers."
        })

    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST, request.FILES, instance=trainer, request=request)
        if form.is_valid():
            # Save the TrainerApplication instance without committing so we can update the user.
            trainer = form.save(commit=False)
            if trainer.user:
                user = trainer.user
                new_username = form.cleaned_data.get("username")
                new_email = form.cleaned_data.get("email")
                new_password = form.cleaned_data.get("password1")
                new_designation = form.cleaned_data.get("designation")
                
                # Update user fields if provided
                if new_username:
                    user.username = new_username
                if new_email:
                    user.email = new_email
                if new_password:
                    user.set_password(new_password)
                if new_designation:
                    user.designation = new_designation
                user.save()
            trainer.save()
            return redirect('manage_trainers')
    else:
        form = TrainerApplicationForm(instance=trainer, request=request)
    return render(request, 'superuser/edit_trainer.html', {
        'form': form,
        'heading': 'Edit Trainer',
        'read_only': False,
    })


@login_required
@user_passes_test(superuser_required)
def delete_trainer(request, trainer_id):
    """
    Deletes a TrainerApplication AND its associated CustomUser.
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)

    if trainer.user:
        trainer.user.delete()
    else:
        trainer.delete()

    return redirect('manage_trainers')

















































































# Add Trainee
@login_required
@user_passes_test(superuser_required)  # Adjust decorator based on required role
def add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Temporarily hold application data without saving
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'  # Set a default or form-defined designation
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user  # Ensure the trainee record is linked correctly
            app_obj.save()

            return redirect('manage_trainees')  # Redirect after successful creation
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







































































































from itertools import chain
from django.db.models import Value, CharField
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import STCReport, ActivityReport, LeaveReport

@login_required
@user_passes_test(superuser_required)
def track_report_submissions(request):
    """
    Shows all approved reports (STC, Activity, and Leave Reports) 
    and allows filtering by start_date and end_date.
    """

    # Fetch all approved STC, Activity, and Leave Reports
    approved_stc_reports = STCReport.objects.filter(status='APPROVED').select_related('prepared_by', 'approved_by')
    approved_activity_reports = ActivityReport.objects.filter(status='APPROVED').select_related('prepared_by', 'approved_by')
    approved_leave_reports = LeaveReport.objects.filter(status='APPROVED').select_related('prepared_by', 'approved_by')

    # Apply filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        approved_stc_reports = approved_stc_reports.filter(created_at__gte=start_date)
        approved_activity_reports = approved_activity_reports.filter(created_at__gte=start_date)
        approved_leave_reports = approved_leave_reports.filter(created_at__gte=start_date)

    if end_date:
        approved_stc_reports = approved_stc_reports.filter(created_at__lte=end_date)
        approved_activity_reports = approved_activity_reports.filter(created_at__lte=end_date)
        approved_leave_reports = approved_leave_reports.filter(created_at__lte=end_date)

    # ✅ Properly annotate report type using Value() function
    approved_stc_reports = approved_stc_reports.annotate(report_type_label=Value('STC Report', output_field=CharField()))
    approved_activity_reports = approved_activity_reports.annotate(report_type_label=Value('Activity Report', output_field=CharField()))
    approved_leave_reports = approved_leave_reports.annotate(report_type_label=Value('Leave Report', output_field=CharField()))

    # Combine reports and sort by created_at (newest first)
    approved_reports = sorted(
        chain(approved_stc_reports, approved_activity_reports, approved_leave_reports), 
        key=lambda report: report.created_at, 
        reverse=True
    )

    context = {
        'approved_reports': approved_reports,
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

########################################
# 1) Administrative User Dashboard
########################################
@login_required
@user_passes_test(administrative_user_required)
def administrativeuser_dashboard(request):
    # 1) Grab ALL cohorts for the dropdown
    all_cohorts = Cohort.objects.all().order_by('name')
    selected_cohort_id = request.GET.get('cohort', 'all')

    # 2) Build the base queryset
    trainees_qs = TraineeApplication.objects.all()
    if selected_cohort_id != 'all':
        # Validate cohort_id
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass  # handle error if needed

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()  # Total "Completed"

    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA ================
    # Per the instructions, this should be the sum of Total Employed + Total Self-Employed (both completed)
    total_in_work = total_self_employed + total_employed

    # For the chart breakdown by sector (female first, then male),
    # we consider only those who are COMPLETED & employed/self-employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # All sectors
    all_sectors = Sector.objects.all().order_by('name')
    sector_gender_list = []
    for sector in all_sectors:
        # Female first, then male
        female_count = in_work_qs.filter(sector=sector, gender="Female").count()
        male_count = in_work_qs.filter(sector=sector, gender="Male").count()
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Female",
            "count": female_count
        })
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Male",
            "count": male_count
        })
    sector_gender_json = json.dumps(sector_gender_list)

    # ================ OUTREACH DATA ================
    # Outreach = all individuals enrolled (any study status in the cohort)
    total_outreach = trainees_qs.count()

    # For the outreach chart by district (female first, then male),
    # we consider ALL individuals in trainees_qs
    all_districts = District.objects.all().order_by('name')
    district_gender_list = []
    for dist in all_districts:
        female_count = trainees_qs.filter(district=dist, gender="Female").count()
        male_count = trainees_qs.filter(district=dist, gender="Male").count()
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Female",
            "count": female_count
        })
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Male",
            "count": male_count
        })
    district_gender_json = json.dumps(district_gender_list)

    # ================ ASSESSMENT DATA ================
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_sector_list = []
    for sector in all_sectors:
        successful_count = successful_assessed_qs.filter(sector=sector).count()
        successful_sector_list.append({
            "sector__name": sector.name,
            "count": successful_count
        })
    successful_sector_json = json.dumps(successful_sector_list)

    context = {
        # For the dropdown
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,

        # Banners (all referencing COMPLETED trainees)
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work
        "total_in_work": total_in_work,
        "sector_gender_data": sector_gender_json,

        # Outreach
        "total_outreach": total_outreach,
        "district_gender_data": district_gender_json,

        # Assessment
        "successful_sector_data": successful_sector_json,
    }

    return render(request, "adminuser/dashboard.html", context)


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
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainer_apps = trainer_apps.filter(name__icontains=search_query)

    return render(request, 'adminuser/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'search_query': search_query,
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
            designation = form.cleaned_data['designation']

            # Create the user in CustomUser
            new_user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                email=email,
                role='TRAINER',      # Force trainer role
                designation=designation,
            )

            # Link the trainer application to the newly created user
            trainer_app.user = new_user  # THIS IS THE MISSING LINE
            trainer_app.save()

            return redirect('admin_manage_trainers')
    else:
        form = TrainerApplicationForm()

    return render(request, 'adminuser/add_trainer.html', {'form': form})


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

    return render(request, 'adminuser/trainer_enrollment_access.html', {'users': users})






@login_required
@user_passes_test(administrative_user_required)
def admin_view_trainer(request, trainer_id):
    """
    Display a read-only view of a TrainerApplication.
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    form = TrainerApplicationEditForm(instance=trainer)
    # Disable all fields for read-only
    for field in form.fields:
        form.fields[field].disabled = True
    return render(request, 'adminuser/single_trainer_form.html', {
        'form': form,
        'heading': 'View Trainer (Read-Only)',
        'read_only': True,
    })

@login_required
@user_passes_test(administrative_user_required)
def admin_edit_trainer(request, trainer_id):
    """
    Allow editing a TrainerApplication (admin view) and update the linked user.
    """
    if not request.user.can_enroll_trainers:
        return render(request, 'adminuser/no_permission copy.html', {
            'message': "You do not have permission to edit trainers."
        })

    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST, request.FILES, instance=trainer, request=request)
        if form.is_valid():
            trainer = form.save(commit=False)
            if trainer.user:
                user = trainer.user
                new_username = form.cleaned_data.get("username")
                new_email = form.cleaned_data.get("email")
                new_password = form.cleaned_data.get("password1")
                new_designation = form.cleaned_data.get("designation")
                
                if new_username:
                    user.username = new_username
                if new_email:
                    user.email = new_email
                if new_password:
                    user.set_password(new_password)
                if new_designation:
                    user.designation = new_designation
                user.save()
            trainer.save()
            return redirect('admin_manage_trainers')
    else:
        form = TrainerApplicationForm(instance=trainer, request=request)
    return render(request, 'adminuser/edit_trainer.html', {
        'form': form,
        'heading': 'Edit Trainer',
        'read_only': False,
    })


@login_required
@user_passes_test(administrative_user_required)
def admin_delete_trainer(request, trainer_id):
    """
    Deletes a TrainerApplication AND its associated CustomUser (Admin version).
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)

    if trainer.user:
        trainer.user.delete()
    else:
        trainer.delete()

    return redirect('admin_manage_trainers')


########################################
# 3) Manage Trainees
########################################
@login_required
@user_passes_test(administrative_user_required)
def admin_manage_trainees(request):
    """
    6) Show existing trainees and a button to add a trainee.
       Also a button to see "trainee enrollment access".
    """
    trainee_users = CustomUser.objects.filter(role='TRAINEE').order_by('username')
    trainee_apps = TraineeApplication.objects.all().order_by('-created_at')
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainee_apps = trainee_apps.filter(applicant_name__icontains=search_query)

    return render(request, 'adminuser/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'search_query': search_query,
    })


@login_required
@user_passes_test(administrative_user_required)
def admin_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user  # Ensure the trainee record is linked correctly
            app_obj.save()

            return redirect('admin_manage_trainees')
    else:
        form = TraineeApplicationForm()
    
    return render(request, 'adminuser/add_trainee.html', {'form': form})


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

    return render(request, 'adminuser/trainee_enrollment_access.html', {'users': users})


@login_required
@user_passes_test(administrative_user_required)
def adminuser_view_trainee(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    form = TraineeApplicationEditForm(instance=trainee)
    # Disable fields in the view if you like:
    for f in form.fields:
        form.fields[f].disabled = True

    return render(request, 'adminuser/single_trainee_form.html', {
        'form': form,
        'heading': 'View Trainee (Read-Only)',
        'read_only': True,
    })

@login_required
@user_passes_test(administrative_user_required)
def adminuser_edit_trainee(request, trainee_id):
    if not request.user.can_enroll_trainees:
        return render(
            request,
            'adminuser/no_permission.html',
            {"message": "You do not have permission to edit trainees."}
        )

    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, instance=trainee, request=request)
        if form.is_valid():
            trainee = form.save(commit=False)
            if trainee.created_by:
                user = trainee.created_by
                new_username = form.cleaned_data.get("username")
                new_email = form.cleaned_data.get("email")
                new_password = form.cleaned_data.get("password1")
                
                if new_username:
                    user.username = new_username
                if new_email:
                    user.email = new_email
                if new_password:
                    user.set_password(new_password)
                user.save()
            trainee.save()
            return redirect('admin_manage_trainees')
    else:
        form = TraineeApplicationForm(instance=trainee, request=request)
    return render(request, 'adminuser/edit_trainee.html', {
        'form': form,
        'heading': 'Edit Trainee',
        'read_only': False,
    })


@login_required
@user_passes_test(administrative_user_required)
def adminuser_delete_trainee(request, trainee_id):
    """
    Deletes a TraineeApplication AND its associated CustomUser (Admin version).
    """
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)

    if trainee.created_by:
        trainee.created_by.delete()
    else:
        trainee.delete()

    return redirect('admin_manage_trainees')




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

    return render(request, 'adminuser/audit_logs.html', {
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
    return render(request, 'adminuser/library_dashboard.html', {
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
    return render(request, 'adminuser/add_library_category.html', {'form': form})


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
    return render(request, 'adminuser/upload_library_document.html', {'form': form})


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
    Shows all approved reports (STC, Activity, and Leave Reports) 
    and allows filtering by start_date and end_date.
    """

    # Fetch all approved STC, Activity, and Leave Reports
    approved_stc_reports = STCReport.objects.filter(status='APPROVED').select_related('prepared_by', 'approved_by')
    approved_activity_reports = ActivityReport.objects.filter(status='APPROVED').select_related('prepared_by', 'approved_by')
    approved_leave_reports = LeaveReport.objects.filter(status='APPROVED').select_related('prepared_by', 'approved_by')

    # Apply filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        approved_stc_reports = approved_stc_reports.filter(created_at__gte=start_date)
        approved_activity_reports = approved_activity_reports.filter(created_at__gte=start_date)
        approved_leave_reports = approved_leave_reports.filter(created_at__gte=start_date)

    if end_date:
        approved_stc_reports = approved_stc_reports.filter(created_at__lte=end_date)
        approved_activity_reports = approved_activity_reports.filter(created_at__lte=end_date)
        approved_leave_reports = approved_leave_reports.filter(created_at__lte=end_date)

    # ✅ Properly annotate report type using Value() function
    approved_stc_reports = approved_stc_reports.annotate(report_type_label=Value('STC Report', output_field=CharField()))
    approved_activity_reports = approved_activity_reports.annotate(report_type_label=Value('Activity Report', output_field=CharField()))
    approved_leave_reports = approved_leave_reports.annotate(report_type_label=Value('Leave Report', output_field=CharField()))

    # Combine reports and sort by created_at (newest first)
    approved_reports = sorted(
        chain(approved_stc_reports, approved_activity_reports, approved_leave_reports), 
        key=lambda report: report.created_at, 
        reverse=True
    )

    context = {
        'approved_reports': approved_reports,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'adminuser/track_report_submissions.html', context)























































































































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
    # 1) Grab ALL cohorts for the dropdown
    all_cohorts = Cohort.objects.all().order_by('name')
    selected_cohort_id = request.GET.get('cohort', 'all')

    # 2) Build the base queryset
    trainees_qs = TraineeApplication.objects.all()
    if selected_cohort_id != 'all':
        # Validate cohort_id
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass  # handle error if needed

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()  # Total "Completed"

    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA ================
    # Per the instructions, this should be the sum of Total Employed + Total Self-Employed (both completed)
    total_in_work = total_self_employed + total_employed

    # For the chart breakdown by sector (female first, then male),
    # we consider only those who are COMPLETED & employed/self-employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # All sectors
    all_sectors = Sector.objects.all().order_by('name')
    sector_gender_list = []
    for sector in all_sectors:
        # Female first, then male
        female_count = in_work_qs.filter(sector=sector, gender="Female").count()
        male_count = in_work_qs.filter(sector=sector, gender="Male").count()
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Female",
            "count": female_count
        })
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Male",
            "count": male_count
        })
    sector_gender_json = json.dumps(sector_gender_list)

    # ================ OUTREACH DATA ================
    # Outreach = all individuals enrolled (any study status in the cohort)
    total_outreach = trainees_qs.count()

    # For the outreach chart by district (female first, then male),
    # we consider ALL individuals in trainees_qs
    all_districts = District.objects.all().order_by('name')
    district_gender_list = []
    for dist in all_districts:
        female_count = trainees_qs.filter(district=dist, gender="Female").count()
        male_count = trainees_qs.filter(district=dist, gender="Male").count()
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Female",
            "count": female_count
        })
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Male",
            "count": male_count
        })
    district_gender_json = json.dumps(district_gender_list)

    # ================ ASSESSMENT DATA ================
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_sector_list = []
    for sector in all_sectors:
        successful_count = successful_assessed_qs.filter(sector=sector).count()
        successful_sector_list.append({
            "sector__name": sector.name,
            "count": successful_count
        })
    successful_sector_json = json.dumps(successful_sector_list)

    context = {
        # For the dropdown
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,

        # Banners (all referencing COMPLETED trainees)
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work
        "total_in_work": total_in_work,
        "sector_gender_data": sector_gender_json,

        # Outreach
        "total_outreach": total_outreach,
        "district_gender_data": district_gender_json,

        # Assessment
        "successful_sector_data": successful_sector_json,
    }

    return render(request, "subadmin/dashboard.html", context)


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
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainer_apps = trainer_apps.filter(name__icontains=search_query)

    return render(request, 'subadmin/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'search_query': search_query,
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
            designation = form.cleaned_data['designation']

            # Create the user
            new_user = CustomUser.objects.create_user(
                username=username,
                password=password1,
                email=email,
                role='TRAINER',
                designation=designation,
            )

            # Link the trainer application to the newly created user
            trainer_app.user = new_user  # THIS IS THE MISSING LINE
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
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainee_apps = trainee_apps.filter(applicant_name__icontains=search_query)

    return render(request, 'subadmin/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'search_query': search_query,
    })




@login_required
@user_passes_test(sub_admin_required)
def subadmin_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user  # Ensure the trainee record is linked correctly
            app_obj.save()

            return redirect('subadmin_manage_trainees')
    else:
        form = TraineeApplicationForm()
    
    return render(request, 'subadmin/add_trainee.html', {'form': form})



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



########################################
# 1) Dashboard
########################################
@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_manager_dashboard(request):
    """
    Displays the same style of dashboard as superuser_dashboard,
    but only for trainees in the epicenter manager’s district.
    """

    # 1) Restrict cohorts to only those that actually have trainees in the manager's district.
    user = request.user
    manager_district = user.district  # The district assigned to the epicenter manager
    
    # Fetch all cohorts (do not filter by trainees)
    all_cohorts = Cohort.objects.all().order_by('name')

    selected_cohort_id = request.GET.get('cohort', 'all')

    # Base queryset: Only trainees in the manager's district
    trainees_qs = TraineeApplication.objects.filter(district=manager_district)

    # If a specific cohort is selected, filter trainees by cohort (even if empty)
    if selected_cohort_id != 'all':
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass  # Ignore invalid cohort IDs
    
    # 2) Build the base queryset, filtering by the manager's district
    trainees_qs = TraineeApplication.objects.filter(district=manager_district)
    if selected_cohort_id != 'all':
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass  # ignore invalid cohort IDs if necessary
    
    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()  # Total "Completed"
    
    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()
    
    # ================ "Youth in Work" DATA ================
    # Sum of Employed + Self-employed among the COMPLETED
    total_in_work = total_self_employed + total_employed
    
    # For the chart breakdown by sector (female first, then male), 
    # again only COMPLETED & employed/self-employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])
    
    all_sectors = Sector.objects.all().order_by('name')
    sector_gender_list = []
    for sector in all_sectors:
        female_count = in_work_qs.filter(sector=sector, gender="Female").count()
        male_count = in_work_qs.filter(sector=sector, gender="Male").count()
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Female",
            "count": female_count
        })
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Male",
            "count": male_count
        })
    sector_gender_json = json.dumps(sector_gender_list)
    
    # ================ OUTREACH DATA ================
    # Outreach = all individuals enrolled (any study status) in the manager’s district
    total_outreach = trainees_qs.count()
    
    # District chart for only that manager’s district:
    # If you want only data from that single district, it doesn’t make much sense to
    # do a district-by-district chart. But if you still want it (for a single bar),
    # you can simply collect the female vs. male count. Or if you want to see all 
    # districts but still only trainees in manager’s district, you can do:
    all_districts = District.objects.filter(pk=manager_district.pk).order_by('name')
    # or if you prefer to show *all* districts anyway, do District.objects.all()
    
    district_gender_list = []
    for dist in all_districts:
        female_count = trainees_qs.filter(district=dist, gender="Female").count()
        male_count = trainees_qs.filter(district=dist, gender="Male").count()
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Female",
            "count": female_count
        })
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Male",
            "count": male_count
        })
    district_gender_json = json.dumps(district_gender_list)
    
    # ================ ASSESSMENT DATA ================
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_sector_list = []
    for sector in all_sectors:
        successful_count = successful_assessed_qs.filter(sector=sector).count()
        successful_sector_list.append({
            "sector__name": sector.name,
            "count": successful_count
        })
    successful_sector_json = json.dumps(successful_sector_list)
    
    # Build the context
    context = {
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,
        
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,
        
        "total_in_work": total_in_work,
        "sector_gender_data": sector_gender_json,
        
        "total_outreach": total_outreach,
        "district_gender_data": district_gender_json,
        
        "successful_sector_data": successful_sector_json,
    }
    
    # Render the same template you use for the superuser dashboard (if that’s acceptable),
    # or use a separate template named 'epicentermanager/dashboard.html'.
    # If you want an identical layout, just reuse 'superuser/dashboard.html':
    # return render(request, "superuser/dashboard.html", context)
    
    return render(request, "epicentermanager/dashboard.html", context)


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
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainer_apps = trainer_apps.filter(name__icontains=search_query)

    return render(request, 'epicentermanager/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'manager_district': manager_district,
        'search_query': search_query,
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
                role='TRAINER',
                designation=form.cleaned_data['designation'],
            )

           # Link the trainer application to the newly created user
            trainer_app.user = new_user  # THIS IS THE MISSING LINE
            trainer_app.save()
            return redirect('epicenter_manage_trainers')
    else:
        form = TrainerApplicationForm(request=request)

    return render(request, 'epicentermanager/add_trainer.html', {'form': form})


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_view_trainer(request, trainer_id):
    """
    Display a read-only view of a TrainerApplication.
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    form = TrainerApplicationEditForm(instance=trainer)
    # Disable all fields for read-only
    for field in form.fields:
        form.fields[field].disabled = True
    return render(request, 'epicentermanager/single_trainer_form.html', {
        'form': form,
        'heading': 'View Trainer (Read-Only)',
        'read_only': True,
    })



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
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainee_apps = trainee_apps.filter(applicant_name__icontains=search_query)

    return render(request, 'epicentermanager/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'manager_district': manager_district,
        'search_query': search_query,
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, request=request)  # Pass request here
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user  # Ensure the trainee record is linked correctly
            app_obj.district = request.user.district  # Force district assignment
            app_obj.save()

            return redirect('epicenter_manage_trainees')
    else:
        form = TraineeApplicationForm(request=request)  # Pass request here
    
    return render(request, 'epicentermanager/add_trainee.html', {'form': form})

@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_view_trainee(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    form = TraineeApplicationEditForm(instance=trainee)
    # Disable fields in the view if you like:
    for f in form.fields:
        form.fields[f].disabled = True

    return render(request, 'epicentermanager/single_trainee_form.html', {
        'form': form,
        'heading': 'View Trainee (Read-Only)',
        'read_only': True,
    })



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
    Displays a dashboard for the Sector Lead, filtered only by the lead's sector.
    Youth-in-work and 'successfully assessed' data are displayed by occupation.
    
    Dynamically selects a template based on the sector name (e.g. 'tourism', 'agriculture', etc.).
    """

    user = request.user
    # Safely handle the sector name in lowercase to avoid any case-sensitivity issues
    sector_str = (user.sector.name or "").lower() if user.sector else ""

    # 1) Cohort filter
    all_cohorts = Cohort.objects.all().order_by('name')
    selected_cohort_id = request.GET.get('cohort', 'all')

    # 2) Base queryset: only trainees in the lead's sector
    trainees_qs = TraineeApplication.objects.filter(sector=user.sector)

    # 3) Apply cohort filter if specified
    if selected_cohort_id != 'all':
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()
    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA (by Occupation) ================
    total_in_work = total_self_employed + total_employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # All occupations in the lead’s sector
    all_occupations = Occupation.objects.filter(sector=user.sector).order_by('name')

    occupation_gender_list = []
    for occ in all_occupations:
        female_count = in_work_qs.filter(occupation=occ, gender="Female").count()
        male_count = in_work_qs.filter(occupation=occ, gender="Male").count()
        occupation_gender_list.append({
            "occupation__name": occ.name,
            "gender": "Female",
            "count": female_count
        })
        occupation_gender_list.append({
            "occupation__name": occ.name,
            "gender": "Male",
            "count": male_count
        })
    occupation_gender_json = json.dumps(occupation_gender_list)

    # ================ OUTREACH DATA ================
    total_outreach = trainees_qs.count()

    # District distribution (only districts present in the queryset)
    unique_districts = District.objects.filter(
        id__in=trainees_qs.values_list('district_id', flat=True)
    ).order_by('name')

    district_gender_list = []
    for dist in unique_districts:
        female_count = trainees_qs.filter(district=dist, gender="Female").count()
        male_count = trainees_qs.filter(district=dist, gender="Male").count()
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Female",
            "count": female_count
        })
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Male",
            "count": male_count
        })
    district_gender_json = json.dumps(district_gender_list)

    # ================ ASSESSMENT DATA (by Occupation) ================
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_occupation_list = []
    for occ in all_occupations:
        successful_count = successful_assessed_qs.filter(occupation=occ).count()
        successful_occupation_list.append({
            "occupation__name": occ.name,
            "count": successful_count
        })
    successful_occupation_json = json.dumps(successful_occupation_list)

    # ================ CONTEXT ================
    context = {
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,

        # Banner metrics
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work (occupation-based)
        "total_in_work": total_in_work,
        "occupation_gender_data": occupation_gender_json,

        # Outreach (district-based)
        "total_outreach": total_outreach,
        "district_gender_data": district_gender_json,

        # Assessment (occupation-based)
        "successful_occupation_data": successful_occupation_json,
    }

    # ========== Dynamically pick a template based on the sector name ==========
    # Convert sector name to lowercase, then check substrings.
    # Example: if user.sector.name = "Tourism" or "TOURISM" => 'tourism_dashboard.html'
    if "tourism" in sector_str:
        template_name = "sectorlead/tourism_dashboard.html"
    elif "agriculture" in sector_str:
        template_name = "sectorlead/agriculture_dashboard.html"
    elif "construction" in sector_str:
        template_name = "sectorlead/construction_dashboard.html"
    else:
        # fallback default if you have other sectors or no match
        template_name = "sectorlead/dashboard.html"

    return render(request, template_name, context)


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
    lead_sector = request.user.sector
    trainer_users = CustomUser.objects.filter(role='TRAINER', sector=lead_sector).order_by('username')
    trainer_apps = TrainerApplication.objects.filter(sector=lead_sector).order_by('-created_at')
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainer_apps = trainer_apps.filter(name__icontains=search_query)

    return render(request, 'sectorlead/manage_trainers.html', {
        'trainer_users': trainer_users,
        'trainer_apps': trainer_apps,
        'lead_sector': lead_sector,
        'search_query': search_query,
    })


@login_required
@user_passes_test(sector_lead_required)
def sector_lead_view_trainer(request, trainer_id):
    """
    Display a read-only view of a TrainerApplication.
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    form = TrainerApplicationEditForm(instance=trainer)
    # Disable all fields for read-only
    for field in form.fields:
        form.fields[field].disabled = True
    return render(request, 'sectorlead/single_trainer_form.html', {
        'form': form,
        'heading': 'View Trainer (Read-Only)',
        'read_only': True,
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
                role='TRAINER',
                designation=form.cleaned_data['designation'],
                sector=lead_sector  # Force the sector on the user record too
            )
            # Link the trainer_app to that user if you have a foreign key in your model
            # E.g. trainer_app.user = new_user
            # Link the trainer application to the newly created user
            trainer_app.user = new_user  # THIS IS THE MISSING LINE
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
def sectorlead_view_trainee(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    form = TraineeApplicationEditForm(instance=trainee)
    # Disable fields in the view if you like:
    for f in form.fields:
        form.fields[f].disabled = True

    return render(request, 'sectorlead/single_trainee_form.html', {
        'form': form,
        'heading': 'View Trainee (Read-Only)',
        'read_only': True,
    })

@login_required
@user_passes_test(sector_lead_required)
def sector_lead_manage_trainees(request):
    """
    Shows only trainees within the sector lead's assigned sector.
    Also a button to add a trainee (if can_enroll_trainees).
    """
    lead_sector = request.user.sector
    trainee_users = CustomUser.objects.filter(role='TRAINEE', sector=lead_sector).order_by('username')
    trainee_apps = TraineeApplication.objects.filter(sector=lead_sector).order_by('-created_at')
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainee_apps = trainee_apps.filter(applicant_name__icontains=search_query)

    return render(request, 'sectorlead/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'lead_sector': lead_sector,
        'search_query': search_query,
    })

@login_required
@user_passes_test(sector_lead_required)
def sector_lead_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user  # Ensure the trainee record is linked correctly
            app_obj.save()

            return redirect('sector_lead_manage_trainees')
    else:
        form = TraineeApplicationForm()
    
    return render(request, 'sectorlead/add_trainee.html', {'form': form})





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












































































































































































































































# trainer_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, HttpResponseForbidden, HttpResponseNotFound
from django.db.models import Q
from django.utils import timezone

from .models import (
    CustomUser,
    TraineeApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument,
    UnifiedReport,
    ReportComment
)
from .forms import (
    TraineeProfileUpdateForm,  # So trainer can update certain fields
    UnifiedReportForm,
    ReportCommentForm
)



########################################
# 1) Dashboard
########################################
@login_required
@user_passes_test(trainer_required)
def trainer_dashboard(request):
    """
    Displays a dashboard for the Trainer, restricted to trainees assigned to this trainer.
    The 'Assessment Statistics' section now shows two bars on the same chart:
      - Successfully Assessed
      - Not Graduated (those registered for DIT but not successful).
    Also shows total DIT-registered trainees in a text box on the left.
    """

    user = request.user

    # 1) Identify the trainer application object
    try:
        trainer_obj = user.trainerapplication
    except TrainerApplication.DoesNotExist:
        # If no TrainerApplication is found, show empty data
        trainer_obj = None

    # 2) Trainer's single occupation (if any)
    trainer_occupation = trainer_obj.occupation if trainer_obj else None

    # 3) Cohorts for the dropdown
    all_cohorts = Cohort.objects.all().order_by('name')
    selected_cohort_id = request.GET.get('cohort', 'all')

    # 4) Base queryset: only trainees assigned to this trainer
    trainees_qs = TraineeApplication.objects.none()
    if trainer_obj:
        trainees_qs = TraineeApplication.objects.filter(assigned_trainer=trainer_obj)

    # If a cohort is selected, filter further
    if selected_cohort_id != 'all':
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()
    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA (by trainer's occupation) ================
    total_in_work = total_self_employed + total_employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # Single occupation label (or "No Occupation")
    occupation_label = trainer_occupation.name if trainer_occupation else "No Occupation"

    # Female vs. male counts among COMPLETED & employed/self-employed, for this single occupation
    female_count = in_work_qs.filter(occupation=trainer_occupation, gender="Female").count()
    male_count = in_work_qs.filter(occupation=trainer_occupation, gender="Male").count()

    occupation_gender_data = [
        {
            "occupation__name": occupation_label,
            "gender": "Female",
            "count": female_count
        },
        {
            "occupation__name": occupation_label,
            "gender": "Male",
            "count": male_count
        }
    ]
    occupation_gender_json = json.dumps(occupation_gender_data)

    # ================ OUTREACH DATA ================
    total_outreach = trainees_qs.count()

    # For outreach chart, we again show the same single occupation + female/male
    female_outreach_count = trainees_qs.filter(occupation=trainer_occupation, gender="Female").count()
    male_outreach_count = trainees_qs.filter(occupation=trainer_occupation, gender="Male").count()

    outreach_occupation_data = [
        {
            "occupation__name": occupation_label,
            "gender": "Female",
            "count": female_outreach_count
        },
        {
            "occupation__name": occupation_label,
            "gender": "Male",
            "count": male_outreach_count
        }
    ]
    outreach_occupation_json = json.dumps(outreach_occupation_data)

    # ================ ASSESSMENT DATA (two bars: successful vs not graduated) ================
    # 1) "Successfully Assessed"
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_count = successful_assessed_qs.filter(occupation=trainer_occupation).count()

    # 2) "Not Graduated" => dit_status="REGISTERED" but final_assessment_status != "SUCCESSFUL"
    not_graduated_count = trainees_qs.filter(
        occupation=trainer_occupation,
        dit_status="REGISTERED"
    ).exclude(final_assessment_status="SUCCESSFUL").count()

    # We store them together for a 2-bar chart on the same x label
    assessment_occupation_data = [
        {
            "occupation__name": occupation_label,
            "successful_count": successful_count,
            "not_graduated_count": not_graduated_count,
        }
    ]
    assessment_occupation_json = json.dumps(assessment_occupation_data)

    # Also get total registered for DIT (any final_assessment_status) so we can show on the left
    registered_for_dit_count = trainees_qs.filter(dit_status="REGISTERED").count()

    # ================ CONTEXT ================
    context = {
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,

        # Banners
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work
        "total_in_work": total_in_work,
        "occupation_gender_data": occupation_gender_json,

        # Outreach
        "total_outreach": total_outreach,
        "outreach_occupation_data": outreach_occupation_json,

        # Assessment
        "assessment_occupation_data": assessment_occupation_json,  # 2-bar data (success vs not graduated)
        "registered_for_dit_count": registered_for_dit_count,
    }

    return render(request, "trainer/dashboard.html", context)



########################################
# 2) Trainees
########################################
from django.core.paginator import Paginator

@login_required
@user_passes_test(trainer_required)
def trainer_view_trainees(request):
    """
    Shows the trainees assigned to the trainer, with search and pagination.
    """
    try:
        current_trainer = TrainerApplication.objects.filter(user=request.user).first()
        if not current_trainer:
            return HttpResponseForbidden("You do not have permission to view trainees.")

        search_query = request.GET.get('search', '').strip()

        assigned_trainees = TraineeApplication.objects.filter(assigned_trainer=current_trainer)

        if search_query:
            assigned_trainees = assigned_trainees.filter(applicant_name__icontains=search_query)

        # Paginate results (30 trainees per page)
        paginator = Paginator(assigned_trainees, 30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    except Exception as e:
        page_obj = []
        print(f"Error fetching trainees: {e}")

    return render(request, 'trainer/view_trainees.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })




@login_required
@user_passes_test(trainer_required)
def trainer_edit_trainee(request, trainee_id):
    """
    Allows the trainer to update limited fields of a single assigned trainee,
    if can_edit_trainees == True and the trainee is assigned to this trainer.
    """
    if not request.user.can_edit_trainees:
        return HttpResponseForbidden("You do not have permission to edit trainees.")

    current_trainer = TrainerApplication.objects.filter(user=request.user).first()
    if not current_trainer:
        return HttpResponseForbidden("No valid trainer application found.")

    trainee_obj = get_object_or_404(
        TraineeApplication,
        id=trainee_id,
        assigned_trainer=current_trainer
    )

    if request.method == 'POST':
        form = TraineeProfileUpdateForm(request.POST, instance=trainee_obj)
        if form.is_valid():
            form.save()
            return redirect('trainer_view_trainees')
    else:
        form = TraineeProfileUpdateForm(instance=trainee_obj)

    return render(request, 'trainer/edit_trainee.html', {
        'form': form,
        'trainee': trainee_obj
    })




########################################
# 4) Training Modules
########################################
@login_required
@user_passes_test(trainer_required)
def trainer_training_modules(request):
    modules = TrainingModule.objects.all().order_by('-created_at')
    return render(request, 'trainer/training_modules.html', {'modules': modules})



@login_required
@user_passes_test(trainer_required)
def trainer_download_training_module(request, module_id):
    """
    Allows the trainer to download training modules securely.
    """
    module = get_object_or_404(TrainingModule, id=module_id)

    if not module.file:
        return HttpResponseNotFound("The requested training module file was not found.")

    file_path = module.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except FileNotFoundError:
        return HttpResponseNotFound("The requested file could not be found.")




# Admin permission view
@login_required
@user_passes_test(administrative_user_required)
def admin_trainer_edit_access(request):
    """
    Admin view to grant trainers edit access to trainee details.
    """
    trainers = CustomUser.objects.filter(role='TRAINER').order_by('username')

    if request.method == 'POST':
        for trainer in trainers:
            field_name = f'edit_{trainer.id}'
            checked = request.POST.get(field_name)
            trainer.can_edit_trainees = bool(checked)
            trainer.save()
        return redirect('admin_trainer_edit_access')

    return render(request, 'adminuser/trainer_edit_access.html', {'trainers': trainers})


# Superuser permission view
@login_required
@user_passes_test(superuser_required)
def superuser_trainer_edit_access(request):
    """
    Superuser view to grant trainers edit access to trainee details.
    """
    trainers = CustomUser.objects.filter(role='TRAINER').order_by('username')

    if request.method == 'POST':
        for trainer in trainers:
            field_name = f'edit_{trainer.id}'
            checked = request.POST.get(field_name)
            trainer.can_edit_trainees = bool(checked)
            trainer.save()
        return redirect('superuser_trainer_edit_access')

    return render(request, 'superuser/trainer_edit_access.html', {'trainers': trainers})



# admin_views.py and superuser_views.py

@login_required
@user_passes_test(administrative_user_required)
def module(request):
    if request.method == 'POST':
        form = TrainingModuleForm(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            module.uploaded_by = request.user
            module.save()
            return redirect('module')
    else:
        form = TrainingModuleForm()

    return render(request, 'adminuser/upload_training_module.html', {'form': form})


@login_required
@user_passes_test(superuser_required)
def superuser_upload_training_module(request):
    if request.method == 'POST':
        form = TrainingModuleForm(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            module.uploaded_by = request.user
            module.save()
            return redirect('superuser_upload_training_module')
    else:
        form = TrainingModuleForm()

    return render(request, 'superuser/upload_training_module.html', {'form': form})




























































































































































































































































from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TraineeApplication, SafeguardingMessage
from .forms import SafeguardingMessageForm
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()

# 1. Trainee views
@login_required
@user_passes_test(trainee_required)
def trainee_dashboard(request):
    """
    Displays a dashboard for the logged-in Trainee, filtering only:
      - The same cohort as the trainee
      - The same occupation as the trainee
      - The same district as the trainee

    No 'cohort filter' is shown, no 'assessment' chart. 
    Only banners, 'youth in work', and 'outreach' charts are displayed.
    """

    user = request.user

    # 1) Identify the TraineeApplication for this user (assuming 1:1 or one main record)
    #    This is how we figure out the trainee's fixed cohort, occupation, and district.
    trainee_app = (
        TraineeApplication.objects.filter(created_by=user).first()
    )
    # If there's no matching application, we'll show an empty dashboard
    if not trainee_app:
        return render(request, "trainee/dashboard.html", {
            "no_data": True  # we can conditionally show a message in template
        })

    # 2) Determine the relevant fields from the Trainee's application
    trainee_cohort = trainee_app.cohort
    trainee_occupation = trainee_app.occupation
    trainee_district = trainee_app.district

    # 3) Build the queryset of "similar" trainees 
    #    (same cohort, same occupation, same district)
    trainees_qs = TraineeApplication.objects.filter(
        cohort=trainee_cohort,
        occupation=trainee_occupation,
        district=trainee_district
    )

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")  
    total_trained = trained_qs.count()
    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA ================
    # Only COMPLETED trainees who are Employed or Self-employed
    total_in_work = total_self_employed + total_employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # We'll show exactly one label: the trainee's own occupation name
    occupation_label = trainee_occupation.name if trainee_occupation else "No Occupation"

    # Count female vs. male in that single occupation & in_work_qs
    female_count = in_work_qs.filter(gender="Female").count()
    male_count = in_work_qs.filter(gender="Male").count()

    occupation_gender_data = [
        {
            "occupation__name": occupation_label,
            "gender": "Female",
            "count": female_count
        },
        {
            "occupation__name": occupation_label,
            "gender": "Male",
            "count": male_count
        }
    ]
    occupation_gender_json = json.dumps(occupation_gender_data)

    # ================ OUTREACH DATA ================
    # All trainees in the same (cohort + occupation + district)
    total_outreach = trainees_qs.count()

    # For the outreach chart, also show female vs. male for the same single occupation
    female_outreach_count = trainees_qs.filter(gender="Female").count()
    male_outreach_count = trainees_qs.filter(gender="Male").count()

    outreach_occupation_data = [
        {
            "occupation__name": occupation_label,
            "gender": "Female",
            "count": female_outreach_count
        },
        {
            "occupation__name": occupation_label,
            "gender": "Male",
            "count": male_outreach_count
        }
    ]
    outreach_occupation_json = json.dumps(outreach_occupation_data)

    # ================ CONTEXT ================
    context = {
        # If you want to show the trainee's cohort name anywhere
        "trainee_cohort_name": trainee_cohort.name if trainee_cohort else "",
        "trainee_district_name": trainee_district.name if trainee_district else "",
        # For "no_data" usage in the template if needed
        "no_data": False,

        # Banners
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work
        "total_in_work": total_in_work,
        "occupation_gender_data": occupation_gender_json,

        # Outreach
        "total_outreach": total_outreach,
        "outreach_occupation_data": outreach_occupation_json,
    }

    return render(request, "trainee/dashboard.html", context)

# 4. Trainee profile and update profile (No changes required)
@login_required
def trainee_profile(request):
    try:
        trainee = TraineeApplication.objects.get(created_by=request.user)
    except TraineeApplication.DoesNotExist:
        return HttpResponse("Trainee profile not found", status=404)

    form = TraineeApplicationEditForm(instance=trainee)
    # Disable all fields so the form is read-only
    for field in form.fields:
        form.fields[field].disabled = True

    return render(request, 'trainee/profile.html', {
        'form': form,
        'heading': 'My Profile (Read-Only)',
        'read_only': True,
    })

def update_trainee_profile(request):
    trainee = TraineeApplication.objects.get(created_by=request.user)
    if request.method == "POST":
        form = TraineeProfileUpdateForm(request.POST, instance=trainee)
        if form.is_valid():
            form.save()
            return redirect('trainee_profile')
    else:
        form = TraineeProfileUpdateForm(instance=trainee)
    
    return render(request, 'trainee/update_profile.html', {'form': form})































































































































































































































@login_required
@user_passes_test(lambda u: u.role == 'TRAINEE')
def safeguarding_welcome(request):
    """
    Simple welcome page for trainees with an “Open Chat” button.
    """
    return render(request, 'trainee/welcome.html')


# views.py

@login_required
@user_passes_test(lambda u: u.role == 'TRAINEE')
def safeguarding_chat(request):
    trainee = get_object_or_404(TraineeApplication, created_by=request.user)
    messages = SafeguardingMessage.objects.filter(trainee=trainee).order_by('timestamp')

    if request.method == "POST":
        form = SafeguardingMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.trainee = trainee
            msg.save()
            # Mark message as read by sender (trainee)
            msg.read_by.add(request.user)
            return redirect('safeguarding_chat')
    else:
        form = SafeguardingMessageForm()

    # Mark messages sent by staff as read by the trainee
    unread_messages = SafeguardingMessage.objects.filter(
        trainee=trainee,
        sender__role__in=['SUB_ADMIN', 'ADMIN']
    ).exclude(read_by=request.user)

    for msg in unread_messages:
        msg.read_by.add(request.user)

    return render(request, 'trainee/chat.html', {
        'messages': messages,
        'form': form
    })




# ===============================
# Safeguarding Officer Views
# ===============================

# In your safeguarding_officer_chat_list view (and stakeholder_chat_list if desired):
@login_required
@user_passes_test(lambda u: u.role == 'SUB_ADMIN' and u.designation == 'Safe Guarding Officer')
def safeguarding_officer_chat_list(request):
    trainees = (
        TraineeApplication.objects
        .filter(safeguardingmessage__isnull=False)
        .distinct()
        .order_by('district__name', 'sector__name', 'occupation__name')
    )

    # Get all trainees who have unread messages for this specific officer
    unread_trainees = SafeguardingMessage.objects.filter(
        sender__role='TRAINEE'
    ).exclude(read_by=request.user) \
    .values_list('trainee_id', flat=True).distinct()

    unread_trainees_set = set(unread_trainees)

    return render(request, 'safeguarding/chat_list.html', {
        'trainees': trainees,
        'is_me_officer': request.user.designation == 'M&E Officer',
        'unread_trainees_set': unread_trainees_set,
    })



@login_required
@user_passes_test(lambda u: u.role == 'SUB_ADMIN' and u.designation == 'Safe Guarding Officer')
def safeguarding_officer_chat(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    messages = SafeguardingMessage.objects.filter(trainee=trainee).order_by('timestamp')

    if request.method == "POST":
        form = SafeguardingMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.trainee = trainee
            message.save()
            # Mark message as read by sender (officer)
            message.read_by.add(request.user)
            return redirect('safeguarding_officer_chat', trainee_id=trainee.id)
    else:
        form = SafeguardingMessageForm()

    # Mark trainee messages as read for this specific officer
    unread_messages = SafeguardingMessage.objects.filter(
        trainee=trainee,
        sender__role='TRAINEE'
    ).exclude(read_by=request.user)

    for msg in unread_messages:
        msg.read_by.add(request.user)

    return render(request, 'safeguarding/chat.html', {
        'trainee': trainee,
        'messages': messages,
        'form': form,
        'user': request.user,
    })




@login_required
@user_passes_test(lambda u: u.designation == 'M&E Officer')
def clear_chats(request, trainee_id):
    """
    Clears all safeguarding messages for a given trainee.
    Only accessible by M&E Officers.
    """
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    SafeguardingMessage.objects.filter(trainee=trainee).delete()
    # After clearing, redirect back to the chat list
    # (Both safeguarding officers and stakeholders use the same clear_chats URL.)
    if hasattr(request.user, 'role') and request.user.role == 'SUB_ADMIN':
        return redirect('safeguarding_officer_chat_list')
    else:
        return redirect('stakeholder_chat_list')


# ===============================
# Stakeholder Views
# ===============================
# Stakeholder designations include: 'M&E Officer', 'Principal', 'Sector Lead', 'Accountant', 'Project Manager'.
@login_required
@user_passes_test(lambda u: (u.designation and u.designation.lower() in ['m&e officer', 'principal', 'sector lead', 'accountant', 'project manager', 'safe guarding officer']) or (u.role and u.role.lower() == 'sector_lead'))
def stakeholder_chat_list(request):
    if request.user.role and request.user.role.lower() == 'sector_lead':
        trainees = (
            TraineeApplication.objects
            .filter(sector=request.user.sector, safeguardingmessage__isnull=False)
            .distinct()
            .order_by('district__name', 'sector__name', 'occupation__name')
        )
    else:
        trainees = (
            TraineeApplication.objects
            .filter(safeguardingmessage__isnull=False)
            .distinct()
            .order_by('district__name', 'sector__name', 'occupation__name')
        )

    # Get all trainees who have unread messages for this specific stakeholder
    unread_trainees = SafeguardingMessage.objects.filter(
        sender__role='TRAINEE'
    ).exclude(read_by=request.user) \
    .values_list('trainee_id', flat=True).distinct()

    unread_trainees_set = set(unread_trainees)

    return render(request, 'stakeholders/chat_list.html', {
        'trainees': trainees,
        'is_me_officer': request.user.designation and request.user.designation.lower() == 'm&e officer',
        'unread_trainees_set': unread_trainees_set
    })





@login_required
@user_passes_test(lambda u: u.role.upper() == 'SECTOR_LEAD' or u.designation in ['M&E Officer', 'Principal', 'Accountant', 'Project Manager'])
def stakeholder_chat(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    messages = SafeguardingMessage.objects.filter(trainee=trainee).order_by('timestamp')

    # Mark trainee messages as read for this specific stakeholder
    unread_messages = SafeguardingMessage.objects.filter(
        trainee=trainee,
        sender__role='TRAINEE'
    ).exclude(read_by=request.user)

    for msg in unread_messages:
        msg.read_by.add(request.user)

    return render(request, 'stakeholders/chat.html', {
        'trainee': trainee,
        'messages': messages,
        'user': request.user,
    })












































































































































































@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_status_list(request):
    """
    Lists all trainees in the Epicenter Manager's district,
    showing their study_status and dit_status. 
    The manager can click 'Update Status' to edit.
    """
    manager_district = request.user.district
    trainees = TraineeApplication.objects.filter(district=manager_district)

    return render(request, 'epicentermanager/trainee_status_list.html', {
        'trainees': trainees
    })


@login_required
@user_passes_test(epicenter_manager_required)
def epicenter_update_status(request, trainee_id):
    """
    Allows the epicenter manager to update a single trainee's 
    study status and DIT status. 
    Only accessible if that trainee is in the manager's district.
    """
    trainee = get_object_or_404(
        TraineeApplication,
        id=trainee_id,
        district=request.user.district
    )

    if request.method == 'POST':
        form = ManagerTraineeStatusForm(request.POST, instance=trainee)
        if form.is_valid():
            form.save()
            return redirect('epicenter_status_list')
    else:
        form = ManagerTraineeStatusForm(instance=trainee)

    return render(request, 'epicentermanager/update_trainee_status.html', {
        'form': form,
        'trainee': trainee,
    })











@login_required
@user_passes_test(sub_admin_required)  # or a custom check for "Academic Registrar" specifically
def registrar_dit_list(request):
    """
    Shows all trainees who have been marked as 'REGISTERED' for DIT
    by an Epicenter Manager, with search functionality.
    """
    # Optionally ensure the user has designation == "Academic Registrar"
    if request.user.designation != "Academic Registrar":
        return HttpResponseForbidden("You are not authorized to access this page.")

    search_query = request.GET.get('search', '').strip()

    registered_trainees = TraineeApplication.objects.filter(
        dit_status="REGISTERED"
    ).order_by('-created_at')

    if search_query:
        registered_trainees = registered_trainees.filter(applicant_name__icontains=search_query)

    return render(request, 'subadmin/registrar_dit_list.html', {
        'registered_trainees': registered_trainees,
        'search_query': search_query,
    })



@login_required
@user_passes_test(sub_admin_required)
def registrar_update_assessment(request, trainee_id):
    """
    Allows the Academic Registrar to set the final assessment status:
    SUCCESSFUL, UNSUCCESSFUL, or ABSENT.
    """
    if request.user.designation != "Academic Registrar":
        return HttpResponseForbidden("You are not authorized to access this page.")

    trainee = get_object_or_404(TraineeApplication, id=trainee_id, dit_status="REGISTERED")
    if request.method == 'POST':
        form = RegistrarAssessmentForm(request.POST, instance=trainee)
        if form.is_valid():
            form.save()
            return redirect('registrar_dit_list')
    else:
        form = RegistrarAssessmentForm(instance=trainee)

    return render(request, 'subadmin/registrar_update_assessment.html', {
        'form': form,
        'trainee': trainee
    })



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TraineeApplication

@login_required
def graduation_list(request):
    """
    Shows all trainees who have been successfully assessed (final_assessment_status = 'SUCCESSFUL'),
    filtered based on the logged-in user's role.
    """
    user = request.user  # Get logged-in user
    graduates = TraineeApplication.objects.filter(final_assessment_status="SUCCESSFUL")

    # Apply filters based on the user's role
    if user.role == "EPICENTER_MANAGER":
        graduates = graduates.filter(district=user.district)
    elif user.role == "TRAINEE":
        graduates = graduates.filter(cohort__in=user.trainee_applications.values_list('cohort', flat=True), district=user.district)
    elif user.role == "TRAINER":
        graduates = graduates.filter(assigned_trainer__user=user)
    elif user.role == "SECTOR_LEAD":
        graduates = graduates.filter(sector=user.sector)

    return render(request, 'graduation_list.html', {'graduates': graduates})












































































































































































































































from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import STCReport, STCActionPlan, STCBudgetLine, STCComment
from .forms import (
    STCBaseInfoForm, STCFieldsForm, STCActionPlanFormSet,
    STCBudgetFormSet, STCCommentForm, STCGrandTotalForm
)


#
# Unified Forms Dashboard
# We combine STC and Activity in the same listing
#
@login_required
def forms_dashboard(request):
    """
    Show all STC, Activity, and Leave reports in a single place:
      - Pending
      - Approved
      - Rejected
      - General Approved (where user is a viewer)
    """

    #
    # STC
    #
    pending_stc = STCReport.objects.filter(
        status__in=['PENDING', 'CHECKED']
    ).filter(
        Q(prepared_by=request.user)
    ).distinct()

    approved_stc = STCReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(prepared_by=request.user) |
        Q(viewers=request.user)
    ).distinct()

    general_approved_stc = STCReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(prepared_by=request.user).distinct()

    rejected_stc = STCReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(prepared_by=request.user)
    ).distinct()

    #
    # Activity
    #
    pending_activity = ActivityReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(prepared_by=request.user)
    ).distinct()

    approved_activity = ActivityReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(prepared_by=request.user) |
        Q(viewers=request.user)
    ).distinct()

    general_approved_activity = ActivityReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(prepared_by=request.user).distinct()

    rejected_activity = ActivityReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(prepared_by=request.user)
    ).distinct()

    #
    # Leave
    #
    pending_leave = LeaveReport.objects.filter(
        status='PENDING'
    ).filter(
        Q(prepared_by=request.user)
    ).distinct()

    approved_leave = LeaveReport.objects.filter(
        status='APPROVED'
    ).filter(
        Q(prepared_by=request.user) |
        Q(viewers=request.user)
    ).distinct()

    general_approved_leave = LeaveReport.objects.filter(
        status='APPROVED',
        viewers=request.user
    ).exclude(prepared_by=request.user).distinct()

    rejected_leave = LeaveReport.objects.filter(
        status='REJECTED'
    ).filter(
        Q(prepared_by=request.user)
    ).distinct()

    context = {
        # STC
        'pending_stc': pending_stc,
        'approved_stc': approved_stc,
        'general_approved_stc': general_approved_stc,
        'rejected_stc': rejected_stc,

        # Activity
        'pending_activity': pending_activity,
        'approved_activity': approved_activity,
        'general_approved_activity': general_approved_activity,
        'rejected_activity': rejected_activity,

        # Leave
        'pending_leave': pending_leave,
        'approved_leave': approved_leave,
        'general_approved_leave': general_approved_leave,
        'rejected_leave': rejected_leave,
    }
    return render(request, 'stc/forms_dashboard.html', context)



@login_required
def stc_submit_report_step1(request):
    """
    Step 1: Choose report type (always STC for now), select approver, checker, viewers.
    On success => create a new STCReport with status='PENDING' in the DB,
    then redirect to step2 with that id.
    """
    if request.method == 'POST':
        form = STCBaseInfoForm(request.POST)
        if form.is_valid():
            # Create the STCReport with the user as prepared_by
            stc = form.save(commit=False)
            stc.report_type = 'STC'
            stc.prepared_by = request.user
            stc.save()
            form.save_m2m()  # for the many-to-many viewers
            return redirect('stc_submit_report_step2', report_id=stc.id)
    else:
        form = STCBaseInfoForm()

    return render(request, 'stc/stc_submit_step1.html', {'form': form})


@login_required
def stc_submit_report_step2(request, report_id):
    stc = get_object_or_404(STCReport, id=report_id, prepared_by=request.user)

    # Instead of forbidding editing when the report is rejected,
    # redirect the user to the read-only detail view.
    if stc.status == 'REJECTED':
        return redirect('stc_detail', report_id=stc.id)

    if request.method == 'POST':
        stc_form = STCFieldsForm(request.POST, instance=stc)
        action_plan_formset = STCActionPlanFormSet(request.POST, instance=stc)

        if stc_form.is_valid() and action_plan_formset.is_valid():
            stc_form.save()
            action_plan_formset.save()
            return redirect('stc_submit_report_step3', report_id=stc.id)
        else:
            # (Optional) Log errors for debugging.
            print("STC Form Errors:", stc_form.errors)
            print("Action Plan Formset Errors:", action_plan_formset.errors)
    else:
        stc_form = STCFieldsForm(instance=stc)
        action_plan_formset = STCActionPlanFormSet(instance=stc)

    context = {
        'stc': stc,
        'stc_form': stc_form,
        'action_plan_formset': action_plan_formset,
    }
    return render(request, 'stc/stc_submit_step2.html', context)





@login_required
def stc_submit_report_step3(request, report_id):
    stc = get_object_or_404(STCReport, id=report_id, prepared_by=request.user)

    # If the report has been rejected, do not allow resubmission;
    # redirect to the read-only detail view.
    if stc.status == 'REJECTED':
        return redirect('stc_detail', report_id=stc.id)

    # Allow editing if the status is DRAFT by converting it to PENDING,
    # or if it's already PENDING.
    if stc.status == 'DRAFT':
        stc.status = 'PENDING'
        stc.save(update_fields=['status'])
    elif stc.status != 'PENDING':
        return HttpResponseForbidden("This report is not editable.")

    if request.method == 'POST':
        budget_formset = STCBudgetFormSet(request.POST, instance=stc)
        grand_total_form = STCGrandTotalForm(request.POST, instance=stc)

        if budget_formset.is_valid() and grand_total_form.is_valid():
            budget_formset.save()
            grand_total_form.save()
            return redirect('forms_dashboard')  # Resubmission complete
        else:
            print("Budget Formset Errors:", budget_formset.errors)
            print("Grand Total Form Errors:", grand_total_form.errors)
    else:
        budget_formset = STCBudgetFormSet(instance=stc)
        grand_total_form = STCGrandTotalForm(instance=stc)

    context = {
        'stc': stc,
        'budget_formset': budget_formset,
        'grand_total_form': grand_total_form,
    }
    return render(request, 'stc/stc_submit_step3.html', context)








@login_required
def stc_detail(request, report_id):
    """
    Standard format view for the STC (like in the screenshots).
    Show tables for Action Plan, Budget, plus comments, etc.
    """
    stc = get_object_or_404(STCReport, id=report_id)
    if not stc.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    comments = stc.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = STCCommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.stc_report = stc
            c.user = request.user
            c.save()
            return redirect('stc_detail', report_id=stc.id)
    else:
        comment_form = STCCommentForm()

    action_plans = stc.action_plans.all()  # already desc by due_date in model
    budget_lines = stc.budget_lines.all()

    context = {
        'stc': stc,
        'action_plans': action_plans,
        'budget_lines': budget_lines,
        'comments': comments,
        'comment_form': comment_form,
        'media_url': settings.MEDIA_URL,  # Add MEDIA_URL to context
    }
    return render(request, 'stc/stc_detail.html', context)


@login_required
def view_reports_awaiting_approval(request):
    """
    Shows all reports (STC, Activity, and Leave) awaiting approval by the logged-in user.
    Includes reports that are either 'PENDING' or 'CHECKED'.
    """
    # Fetch all STC reports assigned to this user as an approver
    pending_stc = STCReport.objects.filter(
        status__in=['PENDING', 'CHECKED'],
        assigned_approver=request.user
    )

    # Fetch all Activity reports assigned to this user as an approver
    pending_activity = ActivityReport.objects.filter(
        status__in=['PENDING', 'CHECKED'],
        assigned_approver=request.user
    )

    # Fetch all Leave reports assigned to this user as an approver
    pending_leave = LeaveReport.objects.filter(
        status__in=['PENDING', 'CHECKED'],
        assigned_approver=request.user
    )

    context = {
        'pending_stc': pending_stc,
        'pending_activity': pending_activity,
        'pending_leave': pending_leave,
    }
    return render(request, 'stc/view_reports_approval.html', context)





@login_required
def view_reports_awaiting_check(request):
    """
    Lists all STCReports with status='PENDING' (or maybe 'PENDING' or 'REJECTED' if you want) 
    where the current user is assigned_checker.
    """
    reports = STCReport.objects.filter(status='PENDING', assigned_checker=request.user)
    return render(request, 'stc/view_reports_check.html', {'reports': reports})


@login_required
def stc_check(request, report_id):
    """
    Allows the assigned checker to mark a report as checked.
    """
    stc = get_object_or_404(STCReport, id=report_id)

    if stc.assigned_checker != request.user:
        return HttpResponseForbidden("You are not assigned to check this report.")

    if request.method == 'POST':
        stc.mark_checked(request.user)  # Change this line
        stc.save(update_fields=['status'])  # Save status change

        return redirect('forms_dashboard')

    return render(request, 'stc/stc_check.html', {'stc': stc})



@login_required
def stc_approve(request, report_id):
    """
    Approver can mark the report as approved and add an approval comment.
    """
    stc = get_object_or_404(STCReport, id=report_id)
    if stc.assigned_approver != request.user:
        return HttpResponseForbidden("You are not assigned as approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            STCComment.objects.create(
                stc_report=stc,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        stc.approve(request.user)
        return redirect('forms_dashboard')

    return render(request, 'stc/approve_report.html', {'stc': stc})


@login_required
def stc_reject(request, report_id):
    """
    Approver (or checker) can reject the report. Must capture a comment.
    The report goes to status='REJECTED', user can then edit/resubmit.
    """
    stc = get_object_or_404(STCReport, id=report_id)
    # Typically only the approver can reject, or maybe checker as well:
    if stc.assigned_approver != request.user and stc.assigned_checker != request.user:
        return HttpResponseForbidden("You are not authorized to reject this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        stc.reject(comment_text, request.user)
        return redirect('forms_dashboard')

    return render(request, 'stc/reject_report.html', {'stc': stc})

from django import forms
from django.shortcuts import render, redirect

class ReportTypeForm(forms.Form):
    REPORT_CHOICES = [
        ('STC', 'STC'),
        ('ACTIVITY', 'Activity'),
        ('LEAVE', 'Leave'),
    ]
    report_type = forms.ChoiceField(choices=REPORT_CHOICES, label="Report Type")

def choose_report_type(request):
    """
    Allows user to pick which type of report to create.
    """
    if request.method == 'POST':
        form = ReportTypeForm(request.POST)
        if form.is_valid():
            rtype = form.cleaned_data['report_type']
            if rtype == 'STC':
                return redirect('stc_submit_report_step1')
            elif rtype == 'ACTIVITY':
                return redirect('activity_submit_report_step1')
            elif rtype == 'LEAVE':
                return redirect('leave_submit_report_step1')
            # In future, add more elif cases for new report types
    else:
        form = ReportTypeForm()
    return render(request, 'stc/choose_report_type.html', {'form': form})


















































































































































































































from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q

from .models import ActivityReport, ActivityComment, ActivityMedia
from .forms import (
    ActivityBaseInfoForm,
    ActivityFieldsForm,
    ActivityCommentForm,
)
from .models import STCReport  # so we can unify the forms_dashboard


#
# Multi-step submission for Activity
#
@login_required
def activity_submit_report_step1(request):
    """
    Step 1: Choose who will approve & who can view the Activity Report.
    """
    if request.method == 'POST':
        form = ActivityBaseInfoForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.prepared_by = request.user
            activity.save()
            form.save_m2m()  # for the viewers many-to-many
            return redirect('activity_submit_report_step2', report_id=activity.id)
    else:
        form = ActivityBaseInfoForm()

    return render(request, 'stc/activity_submit_step1.html', {'form': form})


from django.forms import modelformset_factory

@login_required
def activity_submit_report_step2(request, report_id):
    """
    Step 2: Fill in all activity fields, including optional media attachments.
    """
    activity = get_object_or_404(ActivityReport, id=report_id, prepared_by=request.user)

    if activity.status == 'REJECTED':
        activity.status = 'PENDING'
        activity.save(update_fields=['status'])
    elif activity.status != 'PENDING':
        return HttpResponseForbidden("This report is not editable.")

    if request.method == 'POST':
        form = ActivityFieldsForm(request.POST, instance=activity)

        if form.is_valid():
            form.save()

            # ✅ Handle multiple files manually
            files = request.FILES.getlist('files')
            for file in files:
                ActivityMedia.objects.create(activity_report=activity, file=file)

            return redirect('forms_dashboard')

    else:
        form = ActivityFieldsForm(instance=activity)

    return render(request, 'stc/activity_submit_step2.html', {
        'form': form,
        'activity': activity
    })







#
# Viewing the Activity in standard format


@login_required
def activity_detail(request, report_id):
    activity = get_object_or_404(ActivityReport, id=report_id)
    if not activity.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    comments = activity.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = ActivityCommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.activity_report = activity
            c.user = request.user
            c.save()
            return redirect('activity_detail', report_id=activity.id)
    else:
        comment_form = ActivityCommentForm()

    context = {
        'activity': activity,
        'comments': comments,
        'comment_form': comment_form,
        'media_url': settings.MEDIA_URL,  # Ensure this is included in the context
    }
    return render(request, 'stc/activity_detail.html', context)



#
# Approve / Reject
#
@login_required
def activity_approve(request, report_id):
    activity = get_object_or_404(ActivityReport, id=report_id)
    if activity.assigned_approver != request.user:
        return HttpResponseForbidden("You are not assigned as approver for this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ActivityComment.objects.create(
                activity_report=activity,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        activity.approve(request.user)
        return redirect('forms_dashboard')

    return render(request, 'stc/activity_approve.html', {'activity': activity})


@login_required
def activity_reject(request, report_id):
    activity = get_object_or_404(ActivityReport, id=report_id)
    if activity.assigned_approver != request.user:
        return HttpResponseForbidden("You are not assigned to reject this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        activity.reject(comment_text, request.user)
        return redirect('forms_dashboard')

    return render(request, 'stc/activity_reject.html', {'activity': activity})












































@login_required
@user_passes_test(sub_admin_required)
def sub_view_trainer(request, trainer_id):
    """
    Display a read-only view of a TrainerApplication.
    """
    trainer = get_object_or_404(TrainerApplication, id=trainer_id)
    form = TrainerApplicationEditForm(instance=trainer)
    # Disable all fields for read-only
    for field in form.fields:
        form.fields[field].disabled = True
    return render(request, 'subadmin/single_trainer_form.html', {
        'form': form,
        'heading': 'View Trainer (Read-Only)',
        'read_only': True,
    })





@login_required
@user_passes_test(sub_admin_required)
def sub_view_trainee(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    form = TraineeApplicationEditForm(instance=trainee)
    # Disable fields in the view if you like:
    for f in form.fields:
        form.fields[f].disabled = True

    return render(request, 'subadmin/single_trainee_form.html', {
        'form': form,
        'heading': 'View Trainee (Read-Only)',
        'read_only': True,
    })























































































# Superuser Views
# Superuser Dashboard
@login_required
@user_passes_test(data_entrant_required)
def de_dashboard(request):
    # 1) Grab ALL cohorts for the dropdown
    all_cohorts = Cohort.objects.all().order_by('name')
    selected_cohort_id = request.GET.get('cohort', 'all')

    # 2) Build the base queryset
    trainees_qs = TraineeApplication.objects.all()
    if selected_cohort_id != 'all':
        # Validate cohort_id
        try:
            cohort_id_int = int(selected_cohort_id)
            trainees_qs = trainees_qs.filter(cohort_id=cohort_id_int)
        except ValueError:
            pass  # handle error if needed

    # ================ BANNER DATA (Only COMPLETED) ================
    trained_qs = trainees_qs.filter(study_status="COMPLETED")
    total_trained = trained_qs.count()  # Total "Completed"

    total_self_employed = trained_qs.filter(employment_status="Self-employed").count()
    total_employed = trained_qs.filter(employment_status="Employed").count()
    total_refugees = trained_qs.filter(nationality="Refugee").count()
    total_pwds = trained_qs.filter(pwd=True).count()

    # ================ "Youth in Work" DATA ================
    # Per the instructions, this should be the sum of Total Employed + Total Self-Employed (both completed)
    total_in_work = total_self_employed + total_employed

    # For the chart breakdown by sector (female first, then male),
    # we consider only those who are COMPLETED & employed/self-employed
    in_work_qs = trained_qs.filter(employment_status__in=["Self-employed", "Employed"])

    # All sectors
    all_sectors = Sector.objects.all().order_by('name')
    sector_gender_list = []
    for sector in all_sectors:
        # Female first, then male
        female_count = in_work_qs.filter(sector=sector, gender="Female").count()
        male_count = in_work_qs.filter(sector=sector, gender="Male").count()
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Female",
            "count": female_count
        })
        sector_gender_list.append({
            "sector__name": sector.name,
            "gender": "Male",
            "count": male_count
        })
    sector_gender_json = json.dumps(sector_gender_list)

    # ================ OUTREACH DATA ================
    # Outreach = all individuals enrolled (any study status in the cohort)
    total_outreach = trainees_qs.count()

    # For the outreach chart by district (female first, then male),
    # we consider ALL individuals in trainees_qs
    all_districts = District.objects.all().order_by('name')
    district_gender_list = []
    for dist in all_districts:
        female_count = trainees_qs.filter(district=dist, gender="Female").count()
        male_count = trainees_qs.filter(district=dist, gender="Male").count()
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Female",
            "count": female_count
        })
        district_gender_list.append({
            "district__name": dist.name,
            "gender": "Male",
            "count": male_count
        })
    district_gender_json = json.dumps(district_gender_list)

    # ================ ASSESSMENT DATA ================
    successful_assessed_qs = trainees_qs.filter(final_assessment_status="SUCCESSFUL")
    successful_sector_list = []
    for sector in all_sectors:
        successful_count = successful_assessed_qs.filter(sector=sector).count()
        successful_sector_list.append({
            "sector__name": sector.name,
            "count": successful_count
        })
    successful_sector_json = json.dumps(successful_sector_list)

    context = {
        # For the dropdown
        "all_cohorts": all_cohorts,
        "selected_cohort_id": selected_cohort_id,

        # Banners (all referencing COMPLETED trainees)
        "total_trained": total_trained,
        "total_self_employed": total_self_employed,
        "total_employed": total_employed,
        "total_refugees": total_refugees,
        "total_pwds": total_pwds,

        # Youth in Work
        "total_in_work": total_in_work,
        "sector_gender_data": sector_gender_json,

        # Outreach
        "total_outreach": total_outreach,
        "district_gender_data": district_gender_json,

        # Assessment
        "successful_sector_data": successful_sector_json,
    }

    return render(request, "de/dashboard.html", context)



# Add Trainee
@login_required
@user_passes_test(data_entrant_required)
def de_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Temporarily hold application data without saving
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'  # Set a default or form-defined designation
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user  # Ensure the trainee record is linked correctly
            app_obj.save()

            return redirect('de_manage_trainees')  # Redirect after successful creation
    else:
        form = TraineeApplicationForm()
    
    return render(request, 'de/add_trainee.html', {'form': form})





@login_required
@user_passes_test(data_entrant_required)
def de_manage_trainees(request):
    """
    Show trainees from the same district as the logged-in data entrant.
    """
    user_district = request.user.district  # Ensure the user has a 'district' attribute

    trainee_users = CustomUser.objects.filter(role='TRAINEE', district=user_district).order_by('username')
    trainee_apps = TraineeApplication.objects.filter(district=user_district).order_by('-created_at')
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        trainee_apps = trainee_apps.filter(applicant_name__icontains=search_query)

    return render(request, 'de/manage_trainees.html', {
        'trainee_users': trainee_users,
        'trainee_apps': trainee_apps,
        'user_district': user_district,
        'search_query': search_query,
    })





# Add Trainee
@login_required
@user_passes_test(data_entrant_required)
def de_add_trainee(request):
    """
    Creates a new user with role=TRAINEE and a matching TraineeApplication record.
    Ensures the district is automatically assigned based on the logged-in data entrant.
    """
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, request=request)  # Pass request
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Retrieve trainee user data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Create the trainee user
            new_user = CustomUser.objects.create(
                username=username,
                email=email,
                role='TRAINEE',
                designation='General'
            )
            new_user.set_password(password1)
            new_user.save()

            # Link the trainee application to the new trainee user
            app_obj.created_by = new_user
            app_obj.district = request.user.district  # Assign district automatically
            app_obj.save()

            return redirect('de_manage_trainees')
    else:
        form = TraineeApplicationForm(request=request)  # Pass request to form
    
    return render(request, 'de/add_trainee.html', {'form': form})




@login_required
@user_passes_test(data_entrant_required)
def de_view_trainee(request, trainee_id):
    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    form = TraineeApplicationEditForm(instance=trainee)
    # Disable fields in the view if you like:
    for f in form.fields:
        form.fields[f].disabled = True

    return render(request, 'de/single_trainee_form.html', {
        'form': form,
        'heading': 'View Trainee (Read-Only)',
        'read_only': True,
    })









@login_required
@user_passes_test(data_entrant_required)
def de_edit_trainee(request, trainee_id):
    if not request.user.can_enroll_trainees:
        return render(
            request,
            'de/no_permission.html',
            {"message": "You do not have permission to edit trainees."}
        )

    trainee = get_object_or_404(TraineeApplication, id=trainee_id)
    if request.method == 'POST':
        form = TraineeApplicationForm(request.POST, request.FILES, instance=trainee, request=request)
        if form.is_valid():
            trainee = form.save(commit=False)
            if trainee.created_by:
                user = trainee.created_by
                new_username = form.cleaned_data.get("username")
                new_email = form.cleaned_data.get("email")
                new_password = form.cleaned_data.get("password1")
                
                if new_username:
                    user.username = new_username
                if new_email:
                    user.email = new_email
                if new_password:
                    user.set_password(new_password)
                user.save()
            trainee.save()
            return redirect('de_manage_trainees')
    else:
        form = TraineeApplicationForm(instance=trainee, request=request)

    return render(request, 'de/edit_trainee.html', {
        'form': form,
        'heading': 'Edit Trainee',
        'read_only': False,
    })








































































































from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone

from .models import LeaveReport, LeaveComment
from .forms import (
    LeaveBaseInfoForm, LeaveFieldsForm, LeaveCommentForm
)


#
# Step 1
#
@login_required
def leave_submit_report_step1(request):
    """
    User picks approver, checker, viewers for a new LeaveReport.
    """
    if request.method == 'POST':
        form = LeaveBaseInfoForm(request.POST)
        if form.is_valid():
            leave_obj = form.save(commit=False)
            leave_obj.report_type = 'LEAVE'
            leave_obj.prepared_by = request.user
            leave_obj.status = 'PENDING'
            leave_obj.save()
            form.save_m2m()  # for viewers
            # Go to step 2
            return redirect('leave_submit_report_step2', report_id=leave_obj.id)
    else:
        form = LeaveBaseInfoForm()

    return render(request, 'leave/leave_submit_step1.html', {'form': form})


#
# Step 2
#
@login_required
def leave_submit_report_step2(request, report_id):
    """
    User fills in the actual leave fields (type of leave, dates, etc.).
    If REJECTED, we allow editing/resubmission. If PENDING, we allow editing.
    """
    leave_obj = get_object_or_404(LeaveReport, id=report_id, prepared_by=request.user)

    # If previously REJECTED, we set it back to PENDING on form submission
    if leave_obj.status == 'REJECTED':
        pass  # Let them edit
    elif leave_obj.status not in ['PENDING', 'REJECTED']:
        return HttpResponseForbidden("This report is not editable.")

    if request.method == 'POST':
        form = LeaveFieldsForm(request.POST, instance=leave_obj)
        if form.is_valid():
            leave_instance = form.save(commit=False)
            # If it was REJECTED, we set it back to PENDING on save
            if leave_instance.status == 'REJECTED':
                leave_instance.status = 'PENDING'
            leave_instance.save()
            return redirect('forms_dashboard')  # done filling the leave data
    else:
        form = LeaveFieldsForm(instance=leave_obj)

    return render(request, 'leave/leave_submit_step2.html', {
        'leave_obj': leave_obj,
        'form': form
    })


#
# Detail Page
#
@login_required
def leave_detail(request, report_id):
    """
    Displays the leave form in a standard format, referencing your screenshot layout.
    """
    leave_obj = get_object_or_404(LeaveReport, id=report_id)
    if not leave_obj.can_view(request.user):
        return HttpResponseForbidden("You do not have permission to view this report.")

    comments = leave_obj.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = LeaveCommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.leave_report = leave_obj
            c.user = request.user
            c.save()
            return redirect('leave_detail', report_id=leave_obj.id)
    else:
        comment_form = LeaveCommentForm()

    # Convert comma-separated type_of_leave back to a list
    chosen_leave_types = []
    if leave_obj.type_of_leave:
        chosen_leave_types = leave_obj.type_of_leave.split(',')

    context = {
        'leave_obj': leave_obj,
        'chosen_leave_types': chosen_leave_types,
        'comments': comments,
        'comment_form': comment_form,
        'media_url': settings.MEDIA_URL,  # Added image URL to context
    }
    return render(request, 'leave/leave_detail.html', context)


#
# Approve
#
@login_required
def leave_approve(request, report_id):
    leave_obj = get_object_or_404(LeaveReport, id=report_id)
    if leave_obj.assigned_approver != request.user:
        return HttpResponseForbidden("You are not assigned as approver for this report.")
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            LeaveComment.objects.create(
                leave_report=leave_obj,
                user=request.user,
                comment=f"[APPROVED] {comment_text}"
            )
        leave_obj.approve(request.user)
        return redirect('forms_dashboard')
    return render(request, 'leave/leave_approve.html', {'leave_obj': leave_obj})


#
# Reject
#
@login_required
def leave_reject(request, report_id):
    leave_obj = get_object_or_404(LeaveReport, id=report_id)
    if leave_obj.assigned_approver != request.user and leave_obj.assigned_checker != request.user:
        return HttpResponseForbidden("You are not authorized to reject this report.")
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        leave_obj.reject(comment_text, request.user)
        return redirect('forms_dashboard')
    return render(request, 'leave/leave_reject.html', {'leave_obj': leave_obj})


#
# Check
#
@login_required
def leave_check(request, report_id):
    """
    The checker can mark the report as checked.
    """
    leave_obj = get_object_or_404(LeaveReport, id=report_id)
    if leave_obj.assigned_checker != request.user:
        return HttpResponseForbidden("You are not assigned to check this report.")
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            LeaveComment.objects.create(
                leave_report=leave_obj,
                user=request.user,
                comment=f"[CHECKED] {comment_text}"
            )
        leave_obj.mark_checked(request.user)
        return redirect('forms_dashboard')
    return render(request, 'leave/leave_check.html', {'leave_obj': leave_obj})






























from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from .models import STCReport  # adjust your import if needed

@login_required
def download_approved_pdf(request, report_id):
    """
    Generates a PDF download for an approved STC report.
    """
    stc = get_object_or_404(STCReport, id=report_id)
    if stc.status != 'APPROVED':
        return HttpResponseForbidden("This report is not approved yet.")

    # Prepare the context
    context = {
        'stc': stc,
        'action_plans': stc.action_plans.all(),
        'budget_lines': stc.budget_lines.all(),
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        # This context variable is used by our PDF template to extend a base template.
        'base_template': 'base.html',
    }

    # Render the PDF template to a string
    html_string = render_to_string('stc/pdf_template.html', context)

    # Use request.build_absolute_uri('/') as the base URL for static files (e.g., images)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="approved_report_{stc.id}.pdf"'
    return response


@login_required
def download_activity_pdf(request, report_id):
    """
    Generates a PDF download for an approved Activity Report.
    """
    activity = get_object_or_404(ActivityReport, id=report_id)
    if activity.status != 'APPROVED':
        return HttpResponseForbidden("This report is not approved yet.")

    # Prepare the context for the PDF template
    context = {
        'activity': activity,
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        # The base template can be used for styling if needed.
        'base_template': 'base.html',
    }

    # Render the PDF template to a string
    html_string = render_to_string('stc/activity_pdf_template.html', context)
    # Use request.build_absolute_uri('/') as the base URL for static assets
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="approved_activity_{activity.id}.pdf"'
    return response




@login_required
def download_leave_pdf(request, report_id):
    """
    Generates a PDF download for an approved Leave Report.
    """
    leave_obj = get_object_or_404(LeaveReport, id=report_id)
    if leave_obj.status != 'APPROVED':
        return HttpResponseForbidden("This leave report is not approved yet.")

    # Convert comma-separated type_of_leave back into a list
    chosen_leave_types = []
    if leave_obj.type_of_leave:
        chosen_leave_types = leave_obj.type_of_leave.split(',')

    context = {
        'leave_obj': leave_obj,
        'chosen_leave_types': chosen_leave_types,
        'media_url': settings.MEDIA_URL,  # For the logo URL etc.
    }
    
    # Render the PDF template to a string
    html_string = render_to_string('leave/leave_pdf_template.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="approved_leave_report_{leave_obj.id}.pdf"'
    return response










































@login_required
def export_trainees(request):
    """
    Displays a page with filter drop-downs for Phase, Cohort, District, and Sector.
    The user can:
      - Click “Filter” to update the table below (paginated 50 per page).
      - Click “Clear” to reset the filters.
      - Click “Export CSV” to download a CSV containing all filtered records.
    
    The CSV and the table include the following fields:
       Student Number, Name, Gender, Age, Contact, Completed Training,
       DIT Assessed, Passed DIT, Sector, Occupation, Entrepreneurs, Employed,
       District, Village, Parish, Sub County, Phase, Cohort.
    """
    # Read filter parameters (or empty string if not provided)
    phase_id    = request.GET.get('phase', '')
    cohort_id   = request.GET.get('cohort', '')
    district_id = request.GET.get('district', '')
    sector_id   = request.GET.get('sector', '')

    # Build the queryset
    trainees = TraineeApplication.objects.all()
    if phase_id:
        trainees = trainees.filter(cohort__phase__id=phase_id)
    if cohort_id:
        trainees = trainees.filter(cohort__id=cohort_id)
    if district_id:
        trainees = trainees.filter(district__id=district_id)
    if sector_id:
        trainees = trainees.filter(sector__id=sector_id)

    # If the "export" button was clicked, export a CSV of the filtered data.
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trainees.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Student Number', 'Name', 'Gender', 'Age', 'Contact',
            'Completed Training', 'DIT Assessed', 'Passed DIT',
            'Sector', 'Occupation', 'Entrepreneurs', 'Employed',
            'District', 'Village', 'Parish', 'Sub County',
            'Phase', 'Cohort'
        ])
        for trainee in trainees:
            completed_training = "Yes" if trainee.study_status == "COMPLETED" else "No"
            dit_assessed = "Yes" if trainee.dit_status == "REGISTERED" else "No"
            # Update: Passed DIT is Yes if successful, No otherwise.
            passed_dit = "Yes" if trainee.final_assessment_status == "SUCCESSFUL" else "No"
            entrepreneurs = "Yes" if trainee.employment_status == "Self-employed" else "No"
            employed = "Yes" if trainee.employment_status == "Employed" else "No"
            sector_name = trainee.sector.name if trainee.sector else ""
            occupation_name = trainee.occupation.name if trainee.occupation else ""
            district_name = trainee.district.name if trainee.district else ""
            phase_name = trainee.cohort.phase.name if trainee.cohort and trainee.cohort.phase else ""
            cohort_name = trainee.cohort.name if trainee.cohort else ""
            writer.writerow([
                trainee.student_number,
                trainee.applicant_name,
                trainee.gender,
                trainee.age,
                trainee.phone_contact,
                completed_training,
                dit_assessed,
                passed_dit,
                sector_name,
                occupation_name,
                entrepreneurs,
                employed,
                district_name,
                trainee.village,
                trainee.parish,
                trainee.subcounty,
                phase_name,
                cohort_name,
            ])
        return response

    # Paginate the filtered results: 50 records per page.
    paginator = Paginator(trainees, 50)
    page = request.GET.get('page')
    try:
        trainee_apps = paginator.page(page)
    except PageNotAnInteger:
        trainee_apps = paginator.page(1)
    except EmptyPage:
        trainee_apps = paginator.page(paginator.num_pages)

    # For the filter drop-downs:
    phases = Phase.objects.all()
    # If a phase is selected, limit cohorts to those in that phase.
    if phase_id:
        cohorts = Cohort.objects.filter(phase__id=phase_id)
    else:
        cohorts = Cohort.objects.all()
    districts = District.objects.all()
    sectors = Sector.objects.all()

    context = {
        'trainee_apps': trainee_apps,
        'phases': phases,
        'cohorts': cohorts,
        'districts': districts,
        'sectors': sectors,
        'selected_phase': phase_id,
        'selected_cohort': cohort_id,
        'selected_district': district_id,
        'selected_sector': sector_id,
    }
    return render(request, 'export/export_trainees.html', context)
























@login_required
def dit_registered_export(request):
    """
    Exports a CSV of all students registered for DIT.
    If a search query is provided, it filters the results by applicant name.
    """
    search_query = request.GET.get('search', '')
    # Filter only those with dit_status equal to "REGISTERED"
    queryset = TraineeApplication.objects.filter(dit_status="REGISTERED")
    if search_query:
        queryset = queryset.filter(applicant_name__icontains=search_query)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dit_registered_trainees.csv"'
    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Name', 'Cohort', 'Sector', 'Occupation', 'Study Status', 'Final Assessment'])
    for t in queryset:
        cohort_name = t.cohort.name if t.cohort else 'N/A'
        sector_name = t.sector.name if t.sector else 'N/A'
        occupation_name = t.occupation.name if t.occupation else 'N/A'
        # Use Django's display methods if available
        study_status = t.get_study_status_display() if hasattr(t, 'get_study_status_display') else t.study_status
        final_assessment = t.get_final_assessment_status_display() if hasattr(t, 'get_final_assessment_status_display') else t.final_assessment_status
        writer.writerow([
            t.applicant_name,
            cohort_name,
            sector_name,
            occupation_name,
            study_status,
            final_assessment,
        ])
    return response






















































































import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .utils import import_trainees_from_csv

@login_required
def import_trainees_view(request):
    """
    Renders a form for uploading a CSV file. On POST,
    processes the CSV file and imports trainee data.
    Shows a success message with the number of imported and skipped records.
    """
    message = ""
    if request.method == "POST":
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            message = "No file uploaded."
        else:
            try:
                imported_count, skipped_count = import_trainees_from_csv(csv_file)
                message = f"Successfully imported {imported_count} trainees. Skipped {skipped_count} duplicates."
            except Exception as e:
                message = f"Error during import: {str(e)}"
    return render(request, "import/import_trainees.html", {"message": message})





from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import STCReport, ActivityReport, LeaveReport

@login_required
def stc_delete(request, report_id):
    stc = get_object_or_404(STCReport, id=report_id, prepared_by=request.user)
    if request.method == "POST":
        stc.delete()
        return redirect('forms_dashboard')
    # If not POST, simply redirect back.
    return redirect('forms_dashboard')


@login_required
def activity_delete(request, report_id):
    activity = get_object_or_404(ActivityReport, id=report_id, prepared_by=request.user)
    if request.method == "POST":
        activity.delete()
        return redirect('forms_dashboard')
    return redirect('forms_dashboard')


@login_required
def leave_delete(request, report_id):
    leave = get_object_or_404(LeaveReport, id=report_id, prepared_by=request.user)
    if request.method == "POST":
        leave.delete()
        return redirect('forms_dashboard')
    return redirect('forms_dashboard')






































@login_required
@user_passes_test(superuser_required)
def edit_library_category(request, category_id):
    category = get_object_or_404(LibraryCategory, id=category_id)
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('library_dashboard')
    else:
        form = LibraryCategoryForm(instance=category)
    return render(request, 'superuser/edit_library_category.html', {
        'form': form,
        'category': category,
    })

@login_required
@user_passes_test(superuser_required)
def delete_library_category(request, category_id):
    category = get_object_or_404(LibraryCategory, id=category_id)
    if request.method == 'POST':
        # Delete all documents under the category first
        LibraryDocument.objects.filter(category=category).delete()
        category.delete()
        return redirect('library_dashboard')
    return redirect('library_dashboard')

@login_required
@user_passes_test(superuser_required)
def delete_library_document(request, document_id):
    document = get_object_or_404(LibraryDocument, id=document_id)
    if request.method == 'POST':
        document.delete()
        return redirect('library_dashboard')
    return redirect('library_dashboard')










@login_required
@user_passes_test(administrative_user_required)
def adminuser_edit_library_category(request, category_id):
    category = get_object_or_404(LibraryCategory, id=category_id)
    if request.method == 'POST':
        form = LibraryCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_library_dashboard')
    else:
        form = LibraryCategoryForm(instance=category)
    return render(request, 'adminuser/edit_library_category.html', {
        'form': form,
        'category': category,
    })

@login_required
@user_passes_test(administrative_user_required)
def adminuser_delete_library_category(request, category_id):
    category = get_object_or_404(LibraryCategory, id=category_id)
    if request.method == 'POST':
        LibraryDocument.objects.filter(category=category).delete()
        category.delete()
        return redirect('admin_library_dashboard')
    return redirect('admin_library_dashboard')

@login_required
@user_passes_test(administrative_user_required)
def adminuser_delete_library_document(request, document_id):
    document = get_object_or_404(LibraryDocument, id=document_id)
    if request.method == 'POST':
        document.delete()
        return redirect('admin_library_dashboard')
    return redirect('admin_library_dashboard')





