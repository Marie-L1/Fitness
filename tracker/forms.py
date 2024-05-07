from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Goal, Workout

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        def clean_email(self):
            email = self.cleaned_data["email"]
            return email
        
        def clean(self):
            cleaned_data = super().clean()
            password1 = cleaned_data.get("password1")
            password2 = cleaned_data.get("passowrd2")

            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")

            return cleaned_data     


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["description"]   


# for logging a workoutclass WorkoutForm(forms.ModelForm):
class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["date", "exercise", "duration_minutes", "notes", "weight_amount", "weight_type", "activity_type", "disatnce_miles"]    