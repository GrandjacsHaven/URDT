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
