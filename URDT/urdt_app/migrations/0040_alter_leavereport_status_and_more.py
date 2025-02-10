# Generated by Django 5.0.7 on 2025-02-07 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0039_leavereport_leavecomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavereport',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='leavereport',
            name='total_days',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
    ]
