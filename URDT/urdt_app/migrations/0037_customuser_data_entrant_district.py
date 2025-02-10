# Generated by Django 5.0.7 on 2025-02-06 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0036_activitymedia'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='data_entrant_district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_entrants', to='urdt_app.district'),
        ),
    ]
