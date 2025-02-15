# Generated by Django 5.0.7 on 2025-01-19 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0007_trainerapplication_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('SUPER_USER', 'Super User'), ('ADMINISTRATIVE_USER', 'Admin'), ('SUB_ADMIN', 'Sub Admin'), ('EPICENTER_MANAGER', 'Epicenter Manager'), ('SECTOR_LEAD', 'Sector Lead'), ('DATA_ENTRANT', 'Data Entrant'), ('TRAINER', 'Trainer'), ('TRAINEE', 'Trainee')], default='SECTOR_LEAD', max_length=20),
        ),
    ]
