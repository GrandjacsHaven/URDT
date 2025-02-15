# Generated by Django 5.0.7 on 2025-01-22 22:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0013_traineeapplication_current_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='traineeapplication',
            name='cohort',
            field=models.ForeignKey(blank=True, help_text='Select the cohort for this trainee', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainees', to='urdt_app.cohort'),
        ),
    ]
