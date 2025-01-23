# Generated by Django 5.0.7 on 2025-01-18 21:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0003_remove_sector_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainingsession',
            name='trainer',
        ),
        migrations.AddField(
            model_name='trainerapplication',
            name='occupation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainer_occupations', to='urdt_app.occupation'),
        ),
        migrations.AddField(
            model_name='trainerapplication',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainers', to='urdt_app.sector'),
        ),
        migrations.DeleteModel(
            name='TrainingReport',
        ),
        migrations.DeleteModel(
            name='TrainingSession',
        ),
    ]