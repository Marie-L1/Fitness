from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass
    
    class Meta:
        app_label = "tracker"
        db_table = "tracker_user"

    groups = None
    user_permissions = None


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workouts")
    date = models.DateField()
    exercise = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    weight_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    WEIGHT_CHOICES = [
        ("barbell", "Barbell"),
        ("body_weight", "Body Weight"),
        ("kettlebells", "Kettlebells"),
        ("dumbbells", "Dumbbells")
    ]
    weight_type = models.CharField(max_length=20, choices=WEIGHT_CHOICES, null=True, blank=True)
    ACTIVITY_CHOICES = [
        ("run", "Run"),
        ("walk", "Walk"),
        ("bike", "Bike"),
        ("swim", "Swim"),
        ("hike", "Hike"),
        ("dance", "Dance")
    ]
    WEIGHT_UNIT_CHOICES = [
        ("kg", "Kilograms"),
        ("lbs", "Pounds")
    ]
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_UNIT_CHOICES, default="lbs")
    DISTANCE_UNIT_CHOICES = [
        ("km", "Kilometers"),
        ("mi", "Miles"),
    ]
    distance_unit = models.CharField(max_length=2, choices=DISTANCE_UNIT_CHOICES, default="km", blank=True, null=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, null=True)
    distance_miles = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    calories_burned = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s workout on {self.date}"
    

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    achieved = models.BooleanField(default=False)

    def __str__(self):
        return self.description
    

class WaterIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="water_intake")
    date = models.DateField()
    amount_ml = models.DecimalField(max_digits=6, decimal_places=2)
    amount_oz = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.amount_oz:
            self.amount_oz = self.amount_ml * 0.033814
            super().save(*args, **kwargs)

    def __str__(self):
        return(f"{self.user.username}'s water intake on {self.date}")
    

# mental health section
    
class Emotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emotions")
    date = models.DateField()
    emotion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s emotion on {self.date}"
    

class DailyGratitude(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gratitude_entries")
    date = models.DateField()
    entry = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.user.username}'s gratitude entery on {self.date}"
    

class SelfCareHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="self_care_habits")
    habit = models.CharField(max_length=100)

    def __str__(self):
        return self.habit
    

class EnergyLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="energy_levels")
    date = models.DateField()
    level = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}'s energy level on {self.date}"
    

class Rant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rants")
    date = models.DateField(auto_no_add=True)
    rant = models.TextField()

    def __str__(self):
        return f"Rant by {self.user.username} on {self.date}"