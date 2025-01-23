# Generated by Django 5.0.7 on 2025-01-18 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='can_fill_forms',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='can_enroll_trainees',
            field=models.BooleanField(default=False, help_text='Can enroll trainees'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='can_enroll_trainers',
            field=models.BooleanField(default=False, help_text='Can enroll trainers'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('SUPER_USER', 'Super User'), ('ADMINISTRATIVE_USER', 'Admin'), ('SUB_ADMIN', 'Sub Admin'), ('EPICENTER_MANAGER', 'Epicenter Manager'), ('SECTOR_LEAD', 'Sector Lead'), ('DATA_ENTRANT', 'Data Entrant')], default='SECTOR_LEAD', max_length=20),
        ),
    ]
