from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Goal

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