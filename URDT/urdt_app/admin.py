# admin.py

from django.contrib import admin
from .models import (
    CustomUser,
    Phase,
    Cohort,
    Sector,
    Occupation,
    District,
    TraineeApplication,
    TrainerApplication,
    AuditLog,
    LibraryCategory,
    LibraryDocument,
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'designation', 'can_enroll_trainees', 'can_enroll_trainers')
    search_fields = ('username', 'role')
    list_filter = ('role', 'designation')

@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'phase', 'created_at')
    search_fields = ('name', 'phase__name')
    list_filter = ('phase',)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer_designation')  

@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector')
    search_fields = ('name', 'sector__name')
    list_filter = ('sector',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TraineeApplication)
class TraineeApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'phone_contact', 'sector', 'district', 'created_by', 'created_at')
    search_fields = ('applicant_name', 'phone_contact')
    list_filter = ('sector', 'district', 'created_at')

@admin.register(TrainerApplication)
class TrainerApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_contact', 'district', 'created_at')
    search_fields = ('name', 'phone_contact')
    list_filter = ('district', 'created_at')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action')
    list_filter = ('timestamp',)


@admin.register(LibraryCategory)
class LibraryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(LibraryDocument)
class LibraryDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'uploaded_by__username')


from django.contrib import admin
from .models import (
    STCReport,
    STCActionPlan,
    STCBudgetLine,
    STCComment,
    ActivityReport,
    ActivityComment,
    ActivityMedia,
)

# --- STC Report Admin Setup ---

class STCActionPlanInline(admin.TabularInline):
    model = STCActionPlan
    extra = 0  # No extra blank forms


class STCBudgetLineInline(admin.TabularInline):
    model = STCBudgetLine
    extra = 0


class STCCommentInline(admin.TabularInline):
    model = STCComment
    extra = 0
    readonly_fields = ('created_at',)  # For example, if you want to prevent editing timestamps


@admin.register(STCReport)
class STCReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_name', 'status', 'prepared_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'project_name')
    inlines = [STCActionPlanInline, STCBudgetLineInline, STCCommentInline]
    ordering = ('-created_at',)


# Optionally, if you want to have separate admin pages for these related models,
# you can register them as well. They will then be available in the admin sidebar.
@admin.register(STCActionPlan)
class STCActionPlanAdmin(admin.ModelAdmin):
    list_display = ('stc_report', 'accountable', 'action_step', 'due_date')
    ordering = ('-due_date',)


@admin.register(STCBudgetLine)
class STCBudgetLineAdmin(admin.ModelAdmin):
    list_display = ('stc_report', 'specification', 'total')


@admin.register(STCComment)
class STCCommentAdmin(admin.ModelAdmin):
    list_display = ('stc_report', 'user', 'created_at')
    readonly_fields = ('created_at',)


# --- Activity Report Admin Setup ---

class ActivityCommentInline(admin.TabularInline):
    model = ActivityComment
    extra = 0
    readonly_fields = ('created_at',)


class ActivityMediaInline(admin.TabularInline):
    model = ActivityMedia
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_name', 'status', 'prepared_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'project_name')
    inlines = [ActivityCommentInline, ActivityMediaInline]
    ordering = ('-created_at',)


@admin.register(ActivityComment)
class ActivityCommentAdmin(admin.ModelAdmin):
    list_display = ('activity_report', 'user', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(ActivityMedia)
class ActivityMediaAdmin(admin.ModelAdmin):
    list_display = ('activity_report', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
