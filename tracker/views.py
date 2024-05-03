from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import UserCreationForm


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


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()
            username = user.username
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            form = UserCreationForm()
        return render(request, "register.html", {"form": form})
    

@login_required
def new_goal(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("index")
    else:
        form = GoalForm()
    return render(request, "new_goal.html", {"form":form})