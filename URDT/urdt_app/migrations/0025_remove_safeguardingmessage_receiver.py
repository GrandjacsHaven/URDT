# Generated by Django 5.0.7 on 2025-01-27 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0024_safeguardingmessage_receiver_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='safeguardingmessage',
            name='receiver',
        ),
    ]
