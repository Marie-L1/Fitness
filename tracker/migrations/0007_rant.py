# Generated by Django 5.0.3 on 2024-05-19 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_dailygratitude_emotion_energylevel_selfcarehabit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('rant', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rants', to='tracker.user')),
            ],
        ),
    ]
