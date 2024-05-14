from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import UserCreationForm
import matplotlib.pyplot as plt
import base64
from io import BytesIO


from .models import User, Workout, Goal, WaterIntake
from .forms import WorkoutForm, GoalForm, WaterIntakeForm



def index(request):
    # water intake calculation 
    monthly_intake = WaterIntake.objects.filter(
    date__year=request.year,
    date__month=request.monthly_intake
    ).values("date").annotate(total_intake=Sum("amount_ml"))
      
      # generate monthly graph
    dates = [entry["date"] for entry in monthly_intake]
    intake_values = [entry["total_intake" for entry in monthly_intake]]

    plt.plot(dates, intake_values)
    plt.xlabel("Date")
    plt.ylabel("Water Intake (ml)")
    plt.title("Monthly Water Intake")
    plt.grid(True)

    # convert the plots to image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # embed image into HTML
    graph = base64.b64encode(image_png).decode("utf-8")

    return render(request, "tracker/index.html", {"graph": graph})

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
    return render(request, "tracker/index.html", context)



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
            return render(request, "tracker/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "tracker/login.html")


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
        return render(request, "tracker/register.html", {"form": form})
    

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
    return render(request, "tracker/new_goal.html", {"form":form})

def edit_goal(request, goal_id):
    if request.method == "POST" and request.is_ajax():
        goal = Goal.objects.get(pk=goal_id)
        new_description = request.POST.get("description")
        goal.save()
        return JsonResponse({"description": new_description})
    return JsonResponse({"error": "Invalid request"})


# calculate calories burned per minute of each activity type
def calculated_calories_burned(activity_type, duration_minutes):
    calories_per_minute = {
        "run": 12,
        "walk": 3,
        "bike": 12,
        "swim": 7,
        "hike": 7,
        "dance": 5
    }
    if activity_type in calories_per_minute:
        calories_per_minute_for_activity = calories_per_minute[activity_type]
        return duration_minutes * calories_per_minute_for_activity
    else:
        return None

def log_workout(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.calories_burned = calculated_calories_burned(workout.activity_type, workout.duration_minutes)
            workout.save()
            return redirect("index")
    else:
        form = WorkoutForm()
    return render(request, "tracker/log_workout.html", {"form": form})


def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id) 
    if request.method == "POST":
        workout.delete()
        return redirect("index")
    return redirect("user_profile")    

def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    if request.method == "POST":
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        form = WorkoutForm(instance=workout)
    return render(request, "tracker/edit_workout.html", {"form": form})


def user_profile(request):
    past_workouts = Workout.objects.filter(user=request.user).order_by("-date")
    return render(request, "tracker/user_profile.html", {"past_workouts": past_workouts})


def log_water_intake(request):
    if request.method == "POST":
        form = WaterIntakeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = WaterIntakeForm()
        return render(request, "water_intake.html", {"form": form})