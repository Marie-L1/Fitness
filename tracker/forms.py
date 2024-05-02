from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
            password1 = cleaned_dated.get("password1")
            