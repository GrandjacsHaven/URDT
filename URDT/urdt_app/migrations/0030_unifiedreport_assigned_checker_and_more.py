# Generated by Django 5.0.7 on 2025-02-05 06:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0029_remove_activityplan_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='unifiedreport',
            name='assigned_checker',
            field=models.ForeignKey(blank=True, help_text='The user responsible for checking this report.', limit_choices_to=models.Q(('role__in', ['TRAINER', 'TRAINEE']), _negated=True), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_to_check', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='unifiedreport',
            name='checked_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='unifiedreport',
            name='checked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='approved_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='assigned_approver',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('role__in', ['TRAINER', 'TRAINEE']), _negated=True), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_to_approve', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='attached_report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='urdt_app.unifiedreport'),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='report_file',
            field=models.FileField(blank=True, null=True, upload_to='reports_files/'),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('CHECKED', 'Checked'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='unifiedreport',
            name='viewers',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('role__in', ['TRAINER', 'TRAINEE']), _negated=True), related_name='viewable_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='STCReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output', models.TextField(help_text='Output for the STC report.')),
                ('outcome', models.TextField(help_text='Outcome for the STC report.')),
                ('current_reality', models.TextField(help_text='Current reality text for the STC report.')),
                ('unified_report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stc_report', to='urdt_app.unifiedreport')),
            ],
        ),
        migrations.CreateModel(
            name='STCBudgetLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specification', models.CharField(max_length=255)),
                ('meals_refreshment', models.PositiveIntegerField(default=0)),
                ('accommodation', models.PositiveIntegerField(default=0)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('frequency', models.PositiveIntegerField(default=1)),
                ('total', models.PositiveIntegerField(default=0)),
                ('stc_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budget_lines', to='urdt_app.stcreport')),
            ],
        ),
        migrations.CreateModel(
            name='STCActionPlanLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountable', models.CharField(max_length=255)),
                ('action_step', models.TextField()),
                ('due_date', models.DateField()),
                ('stc_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_plan_lines', to='urdt_app.stcreport')),
            ],
            options={
                'ordering': ['-due_date'],
            },
        ),
    ]
