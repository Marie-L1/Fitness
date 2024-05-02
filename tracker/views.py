from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms


from .models import User, Workout, Goal, GoalForm

# for logging a workoutclass WorkoutForm(forms.ModelForm):
class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["date", "exercise", "duration_minutes", "intensity", "notes"]



def index(request):
    if request.user.is_authenticated:
        workout_history = Workout.objects.filter(user=request.user)
        current_goals= Goal.objects.filter(user=request.user, achieved=False)
    else:
        workout_history = None
        current_goals = None

    context = {
        "workout_history": workout_history,
        "current_goals": current_goals
    }
    return render(request, "index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


