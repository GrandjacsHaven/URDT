# Generated by Django 5.0.7 on 2025-02-07 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0040_alter_leavereport_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='traineeapplication',
            name='student_number',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True),
        ),
    ]
