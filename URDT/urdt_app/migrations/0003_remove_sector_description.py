# Generated by Django 5.0.7 on 2025-01-18 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0002_remove_customuser_can_fill_forms_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sector',
            name='description',
        ),
    ]
