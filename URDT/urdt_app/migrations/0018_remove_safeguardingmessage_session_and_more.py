# Generated by Django 5.0.7 on 2025-01-24 07:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urdt_app', '0017_alter_traineeapplication_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='safeguardingmessage',
            name='session',
        ),
        migrations.RenameField(
            model_name='safeguardingmessage',
            old_name='text',
            new_name='content',
        ),
        migrations.AlterField(
            model_name='safeguardingmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='SafeguardingCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('officer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_safeguarding_cases', to=settings.AUTH_USER_MODEL)),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='safeguarding_cases', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='safeguardingmessage',
            name='case',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='urdt_app.safeguardingcase'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='SafeguardingChatSession',
        ),
    ]
