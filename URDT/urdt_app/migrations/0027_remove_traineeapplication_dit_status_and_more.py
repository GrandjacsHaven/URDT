# Generated by Django 5.0.7 on 2025-01-29 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0026_traineeapplication_dit_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='traineeapplication',
            name='dit_status',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='final_assessment_status',
        ),
        migrations.RemoveField(
            model_name='traineeapplication',
            name='study_status',
        ),
    ]
