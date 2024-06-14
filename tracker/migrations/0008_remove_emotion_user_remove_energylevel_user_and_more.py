# Generated by Django 5.0.3 on 2024-06-14 21:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0007_rant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emotion',
            name='user',
        ),
        migrations.RemoveField(
            model_name='energylevel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='rant',
            name='user',
        ),
        migrations.RemoveField(
            model_name='selfcarehabit',
            name='user',
        ),
        migrations.CreateModel(
            name='MentalHealth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('emotion', models.CharField(blank=True, max_length=100, null=True)),
                ('daily_gratitude', models.TextField(blank=True, max_length=500, null=True)),
                ('self_care_habit', models.CharField(blank=True, max_length=100, null=True)),
                ('energy_level', models.IntegerField(blank=True, null=True)),
                ('rant', models.TextField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mental_health_entries', to='tracker.user')),
            ],
        ),
        migrations.DeleteModel(
            name='DailyGratitude',
        ),
        migrations.DeleteModel(
            name='Emotion',
        ),
        migrations.DeleteModel(
            name='EnergyLevel',
        ),
        migrations.DeleteModel(
            name='Rant',
        ),
        migrations.DeleteModel(
            name='SelfCareHabit',
        ),
    ]