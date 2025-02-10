from django.urls import path
from . import views

urlpatterns = [
    # Logging in and out
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

     # 1) Superuser Dashboard
    path('superuser/dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('dataentrant/dashboard/', views.de_dashboard, name='de_dashboard'),
    
    # 2) Manage users
    path('superuser/users/', views.manage_users, name='manage_users'),
    path('superuser/users/create/', views.create_user_view, name='create_user_view'),
    path("superuser/users/update/<int:user_id>/", views.update_user, name="update_user_view"),
    path("superuser/users/delete/<int:user_id>/", views.delete_user, name="delete_user_view"),

    # 3) Phases & cohorts
    path('superuser/phases/', views.manage_phases, name='manage_phases'),
    path('superuser/phases/<int:phase_id>/add-cohort/', views.add_cohort, name='add_cohort'),
    path('phases/edit/<int:phase_id>/', views.edit_phase, name='edit_phase'),
    path('phases/delete/<int:phase_id>/', views.delete_phase, name='delete_phase'),
    path('cohorts/edit/<int:cohort_id>/', views.edit_cohort, name='edit_cohort'),
    path('cohorts/delete/<int:cohort_id>/', views.delete_cohort, name='delete_cohort'),

    # 4) Sectors & occupations
    path('superuser/sectors/', views.manage_sectors, name='manage_sectors'),
    path('superuser/sectors/add/', views.add_sector, name='add_sector'),
    path('superuser/sectors/<int:sector_id>/add-occupation/', views.add_occupation, name='add_occupation'),
    path('sectors/edit/<int:sector_id>/', views.edit_sector, name='edit_sector'),
    path('sectors/delete/<int:sector_id>/', views.delete_sector, name='delete_sector'),
    path('occupations/edit/<int:occupation_id>/', views.edit_occupation, name='edit_occupation'),
    path('occupations/delete/<int:occupation_id>/', views.delete_occupation, name='delete_occupation'),

    # 5) Districts
    path('superuser/districts/', views.manage_districts, name='manage_districts'),
    path('districts/edit/<int:district_id>/', views.edit_district, name='edit_district'),
    path('districts/delete/<int:district_id>/', views.delete_district, name='delete_district'),

    # 6) Trainees
    path('superuser/trainees/', views.manage_trainees, name='manage_trainees'),
    path('dataentrant/manage/trainees/', views.de_manage_trainees, name='de_manage_trainees'),
    path('superuser/trainees/add/', views.add_trainee, name='add_trainee'),
    path('dataentrant/trainees/add/', views.de_add_trainee, name='de_add_trainee'),
    path('superuser/trainees/enrollment-access/', views.trainee_enrollment_access, name='trainee_enrollment_access'),
    path('trainees/view/<int:trainee_id>/', views.view_trainee, name='view_trainee'),
    path('dataentrant/trainees/view/<int:trainee_id>/', views.de_view_trainee, name='de_view_trainee'),
    path('trainees/edit/<int:trainee_id>/', views.edit_trainee, name='edit_trainee'),
    path('dataentrant/trainees/edit/<int:trainee_id>/', views.de_edit_trainee, name='de_edit_trainee'),
    path('trainees/delete/<int:trainee_id>/', views.delete_trainee, name='delete_trainee'),

    # 7) Trainers
    path('superuser/trainers/', views.manage_trainers, name='manage_trainers'),
    path('superuser/trainers/add/', views.add_trainer, name='add_trainer'),
    path('superuser/trainers/enrollment-access/', views.trainer_enrollment_access, name='trainer_enrollment_access'),
    path('trainers/view/<int:trainer_id>/', views.view_trainer, name='view_trainer'),
    path('trainers/edit/<int:trainer_id>/', views.edit_trainer, name='edit_trainer'),
    path('trainers/delete/<int:trainer_id>/', views.delete_trainer, name='delete_trainer'),

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




    path('track-reports/', views.track_report_submissions, name='track_report_submissions'),






      # Administrative User
    path('adminuser/dashboard/', views.administrativeuser_dashboard, name='administrativeuser_dashboard'),
    
    # Trainers
    path('adminuser/trainers/', views.admin_manage_trainers, name='admin_manage_trainers'),
    path('adminuser/trainers/add/', views.admin_add_trainer, name='admin_add_trainer'),
    path('adminuser/trainers/enrollment-access/', views.admin_trainer_enrollment_access, name='admin_trainer_enrollment_access'),
    path('adminuser/view/<int:trainer_id>/', views.admin_view_trainer, name='admin_view_trainer'),
    path('adminuser/edit/<int:trainer_id>/', views.admin_edit_trainer, name='admin_edit_trainer'),
    path('adminuser/delete/<int:trainer_id>/', views.admin_delete_trainer, name='admin_delete_trainer'),

    # Trainees
    path('adminuser/trainees/', views.admin_manage_trainees, name='admin_manage_trainees'),
    path('adminuser/trainees/add/', views.admin_add_trainee, name='admin_add_trainee'),
    path('adminuser/trainees/enrollment-access/', views.admin_trainee_enrollment_access, name='admin_trainee_enrollment_access'),
    path('subadmin/view/<int:trainee_id>/', views.adminuser_view_trainee, name='adminuser_view_trainee'),
    path('adminuser/trainee/edit/<int:trainee_id>/', views.adminuser_edit_trainee, name='adminuser_edit_trainee'),
    path('adminuser/delete/<int:trainee_id>/', views.adminuser_delete_trainee, name='adminuser_delete_trainee'),



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



  path('subadmin/trainee/view/<int:trainee_id>/', views.sub_view_trainee, name='subadmin_view_trainee'),
  path('subadmin/trainer/view/<int:trainer_id>/', views.sub_view_trainer, name='subadmin_view_trainer'),

   



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
    path('epicenter/view/<int:trainer_id>/', views.epicenter_view_trainer, name='epicenter_view_trainer'),
    

    # Trainees
    path('epicenter/trainees/', views.epicenter_manage_trainees, name='epicenter_manage_trainees'),
    path('epicenter/trainees/add/', views.epicenter_add_trainee, name='epicenter_add_trainee'),
    path('epicenter/trainee/view/<int:trainee_id>/', views.epicenter_view_trainee, name='epicenter_view_trainee'),


    # Track
    path('epicenter/track/', views.epicenter_track_home, name='epicenter_track_home'),
    path('epicenter/track/trainees/', views.epicenter_track_trainees, name='epicenter_track_trainees'),
    path('epicenter/track/trainees/<int:trainee_id>/edit/', views.epicenter_edit_trainee, name='epicenter_edit_trainee'),
    path('epicenter/track/trainers/', views.epicenter_track_trainers, name='epicenter_track_trainers'),
    path('epicenter/track/trainers/<int:trainer_id>/edit/', views.epicenter_edit_trainer, name='epicenter_edit_trainer'),



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
    path('sectorlead/view/<int:trainer_id>/', views. sector_lead_view_trainer, name='sector_lead_view_trainer'),

    # Trainees
    path('sectorlead/trainees/', views.sector_lead_manage_trainees, name='sector_lead_manage_trainees'),
    path('sectorlead/trainees/add/', views.sector_lead_add_trainee, name='sector_lead_add_trainee'),
    path('sectorlead/trainees/view/<int:trainee_id>/', views.sectorlead_view_trainee, name='sectorlead_view_trainee'),



    # Library
    path('sectorlead/library/', views.sector_lead_library_dashboard, name='sector_lead_library_dashboard'),
    path('sectorlead/library/add-category/', views.sector_lead_add_library_category, name='sector_lead_add_library_category'),
    path('sectorlead/library/upload/', views.sector_lead_upload_library_document, name='sector_lead_upload_library_document'),
    path('sectorlead/library/download/<int:doc_id>/', views.sector_lead_download_library_document, name='sector_lead_download_library_document'),











    # Trainer
       # Trainer
    path('trainer/dashboard/', views.trainer_dashboard, name='trainer_dashboard'),

    # Trainees
    path('trainer/trainees/', views.trainer_view_trainees, name='trainer_view_trainees'),
    path('trainer/trainees/<int:trainee_id>/edit/', views.trainer_edit_trainee, name='trainer_edit_trainee'),

    # Training Modules
    path('trainer/training-modules/', views.trainer_training_modules, name='trainer_training_modules'),
    path('trainer/training-modules/download/<int:module_id>/', views.trainer_download_training_module, name='trainer_download_training_module'),
    


      # Admin URL
    path('adminuser/trainee/trainer-edit-access/', views.admin_trainer_edit_access, name='admin_trainer_edit_access'),
    path('adminuser/trainee/trainer-edit-access/', views. adminuser_view_trainee, name='admin_trainer_edit_access'),


    # Superuser URL
    path('superuser/trainer-edit-access/', views.superuser_trainer_edit_access, name='superuser_trainer_edit_access'),


    path('adminuser/upload-training-module/', views.module, name='module'),
    path('superuser/upload-training-module/', views.superuser_upload_training_module, name='superuser_upload_training_module'),








    path('dashboard/', views.trainee_dashboard, name='trainee_dashboard'),
    path('profile/', views.trainee_profile, name='trainee_profile'),
    path('update-profile/', views.update_trainee_profile, name='update_trainee_profile'),
   












    # Epicenter Manager
    path('epicenter/trainees-list/', views.epicenter_status_list, name='epicenter_status_list'),
    path('epicenter/trainees-status/<int:trainee_id>/update/', views.epicenter_update_status, name='epicenter_update_status'),

    # Academic Registrar
    path('registrar/dit-list/', views.registrar_dit_list, name='registrar_dit_list'),
    path('registrar/dit-list/<int:trainee_id>/update/', views.registrar_update_assessment, name='registrar_update_assessment'),

    # Graduation
    path('graduation-list/', views.graduation_list, name='graduation_list'),

    # ... existing URL patterns ...

























































































    # Dashboard
    path('forms-dashboard/', views.forms_dashboard, name='forms_dashboard'),

    # Submit STC (multi-step)
    path('stc/submit/step1/', views.stc_submit_report_step1, name='stc_submit_report_step1'),
    path('stc/submit/step2/<int:report_id>/', views.stc_submit_report_step2, name='stc_submit_report_step2'),
    path('stc/submit/step3/<int:report_id>/', views.stc_submit_report_step3, name='stc_submit_report_step3'),

    # Detail
    path('stc/<int:report_id>/detail/', views.stc_detail, name='stc_detail'),

    # Lists for Approver / Checker
    path('stc/awaiting-approval/', views.view_reports_awaiting_approval, name='view_reports_awaiting_approval'),
    path('stc/awaiting-check/', views.view_reports_awaiting_check, name='view_reports_awaiting_check'),

    # Actions: check, approve, reject
    path('stc/<int:report_id>/check/', views.stc_check, name='stc_check'),
    path('stc/<int:report_id>/approve/', views.stc_approve, name='stc_approve'),
    path('stc/<int:report_id>/reject/', views.stc_reject, name='stc_reject'),

    path('choose-report-type/', views.choose_report_type, name='choose_report_type'),









     # Activity submission
    path('activity/submit/step1/', views.activity_submit_report_step1, name='activity_submit_report_step1'),
    path('activity/submit/step2/<int:report_id>/', views.activity_submit_report_step2, name='activity_submit_report_step2'),

    # Activity detail & actions
    path('activity/<int:report_id>/detail/', views.activity_detail, name='activity_detail'),
    path('activity/<int:report_id>/approve/', views.activity_approve, name='activity_approve'),
    path('activity/<int:report_id>/reject/', views.activity_reject, name='activity_reject'),



























    # Trainee URLs
    path('trainee/welcome/', views.safeguarding_welcome, name='safeguarding_welcome'),
    path('trainee/chat/', views.safeguarding_chat, name='safeguarding_chat'),

    # Safeguarding Officer URLs
    path('safeguarding/chat_list/', views.safeguarding_officer_chat_list, name='safeguarding_officer_chat_list'),
    path('safeguarding/chat/<int:trainee_id>/', views.safeguarding_officer_chat, name='safeguarding_officer_chat'),
    path('safeguarding/clear_chats/<int:trainee_id>/', views.clear_chats, name='clear_chats'),

    # Stakeholder URLs
    path('stakeholders/chat_list/', views.stakeholder_chat_list, name='stakeholder_chat_list'),
    path('stakeholders/chats/<int:trainee_id>/', views.stakeholder_chat, name='stakeholder_chat'),














































      # LEAVE FORM
    path('leave/submit/step1/', views.leave_submit_report_step1, name='leave_submit_report_step1'),
    path('leave/submit/step2/<int:report_id>/', views.leave_submit_report_step2, name='leave_submit_report_step2'),

    path('leave/<int:report_id>/detail/', views.leave_detail, name='leave_detail'),

    path('leave/<int:report_id>/approve/', views.leave_approve, name='leave_approve'),
    path('leave/<int:report_id>/reject/', views.leave_reject, name='leave_reject'),
    path('leave/<int:report_id>/check/', views.leave_check, name='leave_check'),










    path('stc/<int:report_id>/download/', views.download_approved_pdf, name='download_approved_pdf'),
    path('activity/<int:report_id>/download/', views.download_activity_pdf, name='download_activity_pdf'),
    path('leave/<int:report_id>/download/', views.download_leave_pdf, name='download_leave_pdf'),









    path('Trainees/trainee/export/', views.export_trainees, name='export_trainees'),
    path('registrar-dit-export/', views.dit_registered_export, name='registrar_dit_export'),
    path('import-trainees/', views.import_trainees_view, name='import_trainees'),


    path('stc/delete/<int:report_id>/', views.stc_delete, name='stc_delete'),
    path('activity/delete/<int:report_id>/', views.activity_delete, name='activity_delete'),
    path('leave/delete/<int:report_id>/', views.leave_delete, name='leave_delete'),

    path('library/category/edit/<int:category_id>/', views.edit_library_category, name='edit_library_category'),
    path('library/category/delete/<int:category_id>/', views.delete_library_category, name='delete_library_category'),
    path('library/document/delete/<int:document_id>/', views.delete_library_document, name='delete_library_document'),

    path('adminuser/library/category/edit/<int:category_id>/', views.adminuser_edit_library_category, name='admin_edit_library_category'),
    path('adminuser/library/category/delete/<int:category_id>/', views.adminuser_delete_library_category, name='admin_delete_library_category'),
    path('adminuser/library/document/delete/<int:document_id>/', views.adminuser_delete_library_document, name='admin_delete_library_document'),










]








