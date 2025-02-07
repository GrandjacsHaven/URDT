# Generated by Django 5.0.7 on 2025-01-19 23:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0008_alter_customuser_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='traineeapplication',
            name='artisan_name',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='assessments_score',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='attendance_percentage',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='certificate_status',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='cohort',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='completion_status',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='dit_assessed',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='enrollment_date',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='epicenter_manager_name',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='progress_notes',
        ),
        migrations.AddField(
            model_name='traineeapplication',
            name='epicenter_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='epicenter_trainees', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='age',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='assigned_trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainees', to='urdt_app.trainerapplication'),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='block_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='community_leader',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='consent_form_obtained',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trainee_applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='urdt_app.district'),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='family_role',
            field=models.CharField(choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Guardian', 'Guardian'), ('Child', 'Child'), ('Other', 'Other')], max_length=20),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='gender',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='has_smartphone',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='has_vision',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='healthcare_access',
            field=models.CharField(choices=[('Use traditional herbs', 'Use traditional herbs'), ('Go to hospital', 'Go to hospital'), ('Clinic', 'Clinic'), ('Other', 'Other')], max_length=50),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='household_members_above_15',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='household_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='internet_access',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='marital_status',
            field=models.CharField(choices=[('Single', 'Single'), ('Divorced', 'Divorced'), ('Married', 'Married'), ('Widowed', 'Widowed')], max_length=20),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='mentees',
            field=models.TextField(blank=True, help_text='Enter 5 names, one per line or separated by commas.', null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='monthly_income',
            field=models.CharField(choices=[('Below 100,000', 'Below 100,000'), ('100,000 - 299,000', '100,000 - 299,000'), ('300,000 - 500,000', '300,000 - 500,000'), ('Above 500,000', 'Above 500,000')], max_length=30),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='nationality',
            field=models.CharField(choices=[('Ugandan', 'Ugandan'), ('Refugee', 'Refugee')], default='Ugandan', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='nature_of_disability',
            field=models.CharField(blank=True, choices=[('Hearing impairment with speech', 'Hearing impairment with speech'), ('Hard Hearing', 'Hard Hearing'), ('Low Vision', 'Low Vision'), ('Physical Disability', 'Physical Disability'), ('Albinism', 'Albinism'), ('Others', 'Others')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='occupation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainee_occupation', to='urdt_app.occupation'),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='online_platform_awareness',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='parish',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='passport_photo',
            field=models.ImageField(blank=True, null=True, upload_to='trainee_photos/'),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='pwd',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='sector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainee_sector', to='urdt_app.sector'),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='subcounty',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='village',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='traineeapplication',
            name='zone',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
