from django.urls import path
from . import views

urlpatterns = [
    # Logging in and out
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

     # 1) Superuser Dashboard
    path('superuser/dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    
    # 2) Manage users
    path('superuser/users/', views.manage_users, name='manage_users'),
    path('superuser/users/create/', views.create_user_view, name='create_user_view'),

    # 3) Phases & cohorts
    path('superuser/phases/', views.manage_phases, name='manage_phases'),
    path('superuser/phases/<int:phase_id>/add-cohort/', views.add_cohort, name='add_cohort'),

    # 4) Sectors & occupations
    path('superuser/sectors/', views.manage_sectors, name='manage_sectors'),
    path('superuser/sectors/add/', views.add_sector, name='add_sector'),
    path('superuser/sectors/<int:sector_id>/add-occupation/', views.add_occupation, name='add_occupation'),

    # 5) Districts
    path('superuser/districts/', views.manage_districts, name='manage_districts'),

    # 6) Trainees
    path('superuser/trainees/', views.manage_trainees, name='manage_trainees'),
    path('superuser/trainees/add/', views.add_trainee, name='add_trainee'),
    path('superuser/trainees/enrollment-access/', views.trainee_enrollment_access, name='trainee_enrollment_access'),

    # 7) Trainers
    path('superuser/trainers/', views.manage_trainers, name='manage_trainers'),
    path('superuser/trainers/add/', views.add_trainer, name='add_trainer'),
    path('superuser/trainers/enrollment-access/', views.trainer_enrollment_access, name='trainer_enrollment_access'),

    # 8) Audit logs
    path('superuser/audit-logs/', views.audit_logs, name='audit_logs'),

    
    # 10) Library
    path('superuser/library/', views.library_dashboard, name='library_dashboard'),
    path('superuser/library/category/add/', views.add_library_category, name='add_library_category'),
    path('superuser/library/upload/', views.upload_library_document, name='upload_library_document'),
    path('superuser/library/download/<int:doc_id>/', views.download_library_document, name='download_library_document'),
    
    #APIs
    path('api/dynamic-field-filter/', views.dynamic_field_filter, name='dynamic_field_filter'),
    path('api/dynamic-sector-filter/', views.dynamic_sector_filter, name='dynamic_sector_filter'),
    path('api/dynamic-occupation-filter/', views.dynamic_occupation_filter, name='dynamic_occupation_filter'),
    path('api/dynamic-occupation-filter/', views.dynamic_occupation_filter, name='dynamic_occupation_filter'),
    path('api/dynamic-assigned-trainer-filter/', views.dynamic_assigned_trainer_filter, name='dynamic_assigned_trainer_filter'),
    path('api/dynamic-epicenter-manager-filter/', views.dynamic_epicenter_manager_filter, name='dynamic_epicenter_manager_filter'),




    #New forms urls
    path('forms-dashboard/', views.forms_dashboard, name='forms_dashboard'),
    path('submit-report/', views.submit_report, name='submit_report'),
    path('view-submitted-reports/', views.view_submitted_reports, name='view_submitted_reports'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('report/<int:report_id>/approve/', views.report_approve, name='report_approve'),
    path('report/<int:report_id>/reject/', views.report_reject, name='report_reject'),
    path('report/<int:report_id>/download-file/', views.download_report_file, name='download_report_file'),
    path('track-reports/', views.track_report_submissions, name='track_report_submissions'),






      # Administrative User
    path('adminuser/dashboard/', views.administrativeuser_dashboard, name='administrativeuser_dashboard'),
    
    # Trainers
    path('adminuser/trainers/', views.admin_manage_trainers, name='admin_manage_trainers'),
    path('adminuser/trainers/add/', views.admin_add_trainer, name='admin_add_trainer'),
    path('adminuser/trainers/enrollment-access/', views.admin_trainer_enrollment_access, name='admin_trainer_enrollment_access'),

    # Trainees
    path('adminuser/trainees/', views.admin_manage_trainees, name='admin_manage_trainees'),
    path('adminuser/trainees/add/', views.admin_add_trainee, name='admin_add_trainee'),
    path('adminuser/trainees/enrollment-access/', views.admin_trainee_enrollment_access, name='admin_trainee_enrollment_access'),

    # Forms
    path('adminuser/forms/', views.admin_forms_dashboard, name='admin_forms_dashboard'),
    path('adminuser/forms/submit/', views.admin_submit_report, name='admin_submit_report'),
    path('adminuser/forms/submitted/', views.admin_view_submitted_reports, name='admin_view_submitted_reports'),
    path('adminuser/forms/report/<int:report_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('adminuser/forms/report/<int:report_id>/approve/', views.admin_report_approve, name='admin_report_approve'),
    path('adminuser/forms/report/<int:report_id>/reject/', views.admin_report_reject, name='admin_report_reject'),
    path('adminuser/forms/report/<int:report_id>/download/', views.admin_download_report_file, name='admin_download_report_file'),

    # Audit Logs
    path('adminuser/audit-logs/', views.admin_audit_logs, name='admin_audit_logs'),

    # Library
    path('adminuser/library/', views.admin_library_dashboard, name='admin_library_dashboard'),
    path('adminuser/library/add-category/', views.admin_add_library_category, name='admin_add_library_category'),
    path('adminuser/library/upload/', views.admin_upload_library_document, name='admin_upload_library_document'),
    path('adminuser/library/download/<int:doc_id>/', views.admin_download_library_document, name='admin_download_library_document'),

    # Track Report Submissions
    path('adminuser/track-reports/', views.admin_track_report_submissions, name='admin_track_report_submissions'),









    # SUB_ADMIN
    path('subadmin/dashboard/', views.subadmin_dashboard, name='subadmin_dashboard'),

    # Trainers
    path('subadmin/trainers/', views.subadmin_manage_trainers, name='subadmin_manage_trainers'),
    path('subadmin/trainers/add/', views.subadmin_add_trainer, name='subadmin_add_trainer'),

    # Trainees
    path('subadmin/trainees/', views.subadmin_manage_trainees, name='subadmin_manage_trainees'),
    path('subadmin/trainees/add/', views.subadmin_add_trainee, name='subadmin_add_trainee'),

    # Forms
    path('subadmin/forms/', views.subadmin_forms_dashboard, name='subadmin_forms_dashboard'),
    path('subadmin/forms/submit/', views.subadmin_submit_report, name='subadmin_submit_report'),
    path('subadmin/forms/submitted/', views.subadmin_view_submitted_reports, name='subadmin_view_submitted_reports'),
    path('subadmin/forms/report/<int:report_id>/', views.subadmin_report_detail, name='subadmin_report_detail'),
    path('subadmin/forms/report/<int:report_id>/approve/', views.subadmin_report_approve, name='subadmin_report_approve'),
    path('subadmin/forms/report/<int:report_id>/reject/', views.subadmin_report_reject, name='subadmin_report_reject'),
    path('subadmin/forms/report/<int:report_id>/download/', views.subadmin_download_report_file, name='subadmin_download_report_file'),

    # Audit Logs
    path('subadmin/audit-logs/', views.subadmin_audit_logs, name='subadmin_audit_logs'),

    # Library
    path('subadmin/library/', views.subadmin_library_dashboard, name='subadmin_library_dashboard'),
    path('subadmin/library/add-category/', views.subadmin_add_library_category, name='subadmin_add_library_category'),
    path('subadmin/library/upload/', views.subadmin_upload_library_document, name='subadmin_upload_library_document'),
    path('subadmin/library/download/<int:doc_id>/',views.subadmin_download_library_document, name='subadmin_download_library_document'),







    # EPICENTER MANAGER
     # Epicenter Manager
    path('epicenter/dashboard/', views.epicenter_manager_dashboard, name='epicenter_manager_dashboard'),

    # Trainers
    path('epicenter/trainers/', views.epicenter_manage_trainers, name='epicenter_manage_trainers'),
    path('epicenter/trainers/add/', views.epicenter_add_trainer, name='epicenter_add_trainer'),

    # Trainees
    path('epicenter/trainees/', views.epicenter_manage_trainees, name='epicenter_manage_trainees'),
    path('epicenter/trainees/add/', views.epicenter_add_trainee, name='epicenter_add_trainee'),

    # Track
    path('epicenter/track/', views.epicenter_track_home, name='epicenter_track_home'),
    path('epicenter/track/trainees/', views.epicenter_track_trainees, name='epicenter_track_trainees'),
    path('epicenter/track/trainees/<int:trainee_id>/edit/', views.epicenter_edit_trainee, name='epicenter_edit_trainee'),
    path('epicenter/track/trainers/', views.epicenter_track_trainers, name='epicenter_track_trainers'),
    path('epicenter/track/trainers/<int:trainer_id>/edit/', views.epicenter_edit_trainer, name='epicenter_edit_trainer'),

    # Forms
    path('epicenter/forms/', views.epicenter_forms_dashboard, name='epicenter_forms_dashboard'),
    path('epicenter/forms/submit/', views.epicenter_submit_report, name='epicenter_submit_report'),
    path('epicenter/forms/submitted/', views.epicenter_view_submitted_reports, name='epicenter_view_submitted_reports'),
    path('epicenter/forms/report/<int:report_id>/', views.epicenter_report_detail, name='epicenter_report_detail'),
    path('epicenter/forms/report/<int:report_id>/approve/',views.epicenter_report_approve, name='epicenter_report_approve'),
    path('epicenter/forms/report/<int:report_id>/reject/', views.epicenter_report_reject, name='epicenter_report_reject'),
    path('epicenter/forms/report/<int:report_id>/download/', views.epicenter_download_report_file, name='epicenter_download_report_file'),

    # Library
    path('epicenter/library/', views.epicenter_library_dashboard, name='epicenter_library_dashboard'),
    path('epicenter/library/add-category/', views.epicenter_add_library_category, name='epicenter_add_library_category'),
    path('epicenter/library/upload/', views.epicenter_upload_library_document, name='epicenter_upload_library_document'),
    path('epicenter/library/download/<int:doc_id>/', views.epicenter_download_library_document, name='epicenter_download_library_document'),





    # Sector Lead
    path('sectorlead/dashboard/', views.sector_lead_dashboard, name='sector_lead_dashboard'),

    # Trainers
    path('sectorlead/trainers/', views.sector_lead_manage_trainers, name='sector_lead_manage_trainers'),
    path('sectorlead/trainers/add/', views.sector_lead_add_trainer, name='sector_lead_add_trainer'),

    # Trainees
    path('sectorlead/trainees/', views.sector_lead_manage_trainees, name='sector_lead_manage_trainees'),
    path('sectorlead/trainees/add/', views.sector_lead_add_trainee, name='sector_lead_add_trainee'),

    # Forms
    path('sectorlead/forms/', views.sector_lead_forms_dashboard, name='sector_lead_forms_dashboard'),
    path('sectorlead/forms/submit/', views.sector_lead_submit_report, name='sector_lead_submit_report'),
    path('sectorlead/forms/submitted/', views.sector_lead_view_submitted_reports, name='sector_lead_view_submitted_reports'),
    path('sectorlead/forms/report/<int:report_id>/', views.sector_lead_report_detail, name='sector_lead_report_detail'),
    path('sectorlead/forms/report/<int:report_id>/approve/', views.sector_lead_report_approve, name='sector_lead_report_approve'),
    path('sectorlead/forms/report/<int:report_id>/reject/', views.sector_lead_report_reject, name='sector_lead_report_reject'),
    path('sectorlead/forms/report/<int:report_id>/download/', views.sector_lead_download_report_file, name='sector_lead_download_report_file'),

    # Library
    path('sectorlead/library/', views.sector_lead_library_dashboard, name='sector_lead_library_dashboard'),
    path('sectorlead/library/add-category/', views.sector_lead_add_library_category, name='sector_lead_add_library_category'),
    path('sectorlead/library/upload/', views.sector_lead_upload_library_document, name='sector_lead_upload_library_document'),
    path('sectorlead/library/download/<int:doc_id>/', views.sector_lead_download_library_document, name='sector_lead_download_library_document'),


]



