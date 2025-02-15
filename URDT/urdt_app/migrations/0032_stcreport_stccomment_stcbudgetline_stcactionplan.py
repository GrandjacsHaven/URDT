# Generated by Django 5.0.7 on 2025-02-05 10:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0031_remove_stcbudgetline_stc_report_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='STCReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(default='STC', max_length=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CHECKED', 'Checked'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateField(blank=True, null=True)),
                ('checked_at', models.DateField(blank=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('output', models.TextField(blank=True)),
                ('outcome', models.TextField(blank=True)),
                ('current_reality', models.TextField(blank=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stc_approved_reports', to=settings.AUTH_USER_MODEL)),
                ('assigned_approver', models.ForeignKey(blank=True, limit_choices_to=models.Q(('role__in', ['TRAINER', 'TRAINEE']), _negated=True), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stc_reports_to_approve', to=settings.AUTH_USER_MODEL)),
                ('assigned_checker', models.ForeignKey(blank=True, limit_choices_to=models.Q(('role__in', ['TRAINER', 'TRAINEE']), _negated=True), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stc_reports_to_check', to=settings.AUTH_USER_MODEL)),
                ('checked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stc_checked_reports', to=settings.AUTH_USER_MODEL)),
                ('prepared_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stc_prepared_reports', to=settings.AUTH_USER_MODEL)),
                ('viewers', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('role__in', ['TRAINER', 'TRAINEE']), _negated=True), related_name='stc_viewable_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='STCComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('stc_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='urdt_app.stcreport')),
            ],
        ),
        migrations.CreateModel(
            name='STCBudgetLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specification', models.CharField(max_length=255)),
                ('meals_and_refreshment', models.CharField(blank=True, max_length=100)),
                ('accommodation', models.CharField(blank=True, max_length=100)),
                ('amount', models.CharField(blank=True, max_length=100)),
                ('frequency', models.CharField(blank=True, max_length=100)),
                ('total', models.CharField(blank=True, max_length=100)),
                ('stc_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budget_lines', to='urdt_app.stcreport')),
            ],
        ),
        migrations.CreateModel(
            name='STCActionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountable', models.CharField(max_length=255)),
                ('action_step', models.TextField()),
                ('due_date', models.DateField()),
                ('stc_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_plans', to='urdt_app.stcreport')),
            ],
            options={
                'ordering': ['-due_date'],
            },
        ),
    ]
