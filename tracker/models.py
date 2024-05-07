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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="water")
    date = models.DateField()
    amount_ml = models.IntegerField()

    def __str__(self):
        return(f"{self.user.username}'s water intake on {self.date}")