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
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exercise': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'weight_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 'o'}),
            'distance_miles': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }

    def clean_duration_minutes(self):
        duration_minutes = self.cleaned_data.get('duration_minutes')
        if duration_minutes <= 0:
            raise forms.ValidationError("Duration must be a positive number.")
        return duration_minutes
    
    def clean_weight_amount(self):
        weight_amount = self.cleaned_data.get('weight_amount')
        if weight_amount < 0:
            raise forms.ValidationError("Weight amount must be a positive number.")
        return weight_amount
    
    def clean_distance_miles(self):
        distance_miles = self.cleaned_data.get('distance_miles')
        if distance_miles is not None and distance_miles < 0:
            raise forms.ValidationError("The distance must be a positive number.")