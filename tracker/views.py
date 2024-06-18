from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.db.models import Sum, Count, Avg
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpRequest
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Sum
import matplotlib.pyplot as plt
import base64
from io import BytesIO, StringIO
import logging
from collections import Counter
import calendar
from collections import defaultdict
from datetime import datetime
import numpy as np    # for array manipulation
import json

logger = logging.getLogger(__name__)
User = get_user_model()

from .models import User, Workout, Goal, WaterIntake, MentalHealth
from .forms import WorkoutForm, GoalForm, WaterIntakeForm, RegistrationForm, MentalHealthForm

def index(request):
    if request.user.is_authenticated:
        return redirect("tracker:homepage")
    return render(request, "index.html")


def generate_water_intake_graph(user, month):
    today = datetime.now().date()
    current_month = datetime.now().month

    # Generating monthly water intake graph
    monthly_intake = WaterIntake.objects.filter(user=user, date__year=today.year, date__month=current_month).values("date").annotate(total_intake=Sum("amount_ml"))
    dates = [entry["date"] for entry in monthly_intake]
    intake_values = [entry["total_intake"] for entry in monthly_intake]

    plt.plot(dates, intake_values)
    plt.xlabel("Date")
    plt.ylabel("Water Intake (ml)")
    plt.title("Monthly Water Intake")
    plt.grid(True)

    # Convert the plot to image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode("utf-8")
    plt.close()

    return graph


def generate_heatmap_data(user):
    current_month = timezone.now().month
    
    # Fetching water intake data for the current month
    logged_dates = WaterIntake.objects.filter(user=user, date__month=current_month).dates("date", "day")
    
    # Initialize heatmap data dictionary
    heatmap_data = {date.day: 0 for date in logged_dates}
    
    # Normalize heatmap data for color intensity
    max_intensity = max(heatmap_data.values(), default=1)
    heatmap_data_list = [{'day': day, 'color_value': heatmap_data.get(day, 0) / max_intensity} for day in range(1, timezone.now().day + 1)]
    
    return heatmap_data_list


def generate_emotion_chart(user):
    current_month = datetime.now().month

    emotions = MentalHealth.objects.filter(user=user, date__month=current_month).values("entry").annotate(count=Count("entry"))
    emotion_data = {entry["entry"]: entry["count"] for entry in emotions}
    labels = list(emotion_data.keys())
    sizes = list(emotion_data.values())
    colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]

    fig, ax = plt.subplots()
    ax.pie(sizes, lables=labels, autopct="%1.1f%%", startangle=90, colors=colors)
    ax.axis("equal")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    chart = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return chart


def generate_energy_level_graph(user):
    current_month = datetime.now().month

    energy_levels = MentalHealth.objects.filter(user=user, date__month=current_month).values("date","energy_level").annotate(count=Count("date"))
    dates = [entry["date"] for entry in energy_levels]
    levels = [entry["energy_level"] for entry in energy_levels]

    plt.figure()
    plt.plot(dates, levels)
    plt.xlabel("Date")
    plt.ylabel("Daily Energy Level")
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    graph = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return graph



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        print(f"Attempting to authenticate user: {username}")   # debugging

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print("Authenticate successful.")   # debugging
            return redirect("tracker:homepage")
        else:
            print("Authentication failed.") # debugging
            messages.error(request, "Invalid username or password.")
        
    return render(request, "login.html")


@login_required(login_url='/tracker/login/')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('tracker:login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})



@login_required(login_url='/tracker/login/')
def homepage(request):
    user = request.user
    print(f"User: {user}, ID: {user.id}")   # Debugging

    today = timezone.now().date()
    current_month = timezone.now().month
    current_month_name = timezone.now().strftime('%B')

    # Fetching current goals (if any)
    current_goals = Goal.objects.filter(user=user, achieved=False)

    # Fetching daily water intake
    daily_intake = WaterIntake.objects.filter(user=user, date=today)
    daily_intake_ml = daily_intake.aggregate(total_intake=Sum("amount_ml"))["total_intake"] or 0

    # Generate monthly water intake graph
    graph = generate_water_intake_graph(user, current_month)

    # Fetching daily emotion logged for today
    today_emotion_entry = MentalHealth.objects.filter(user=user, date=today).first()
    today_emotion = today_emotion_entry.emotion if today_emotion_entry else None

    # Generating heatmap data for the current month
    heatmap_data_list = generate_heatmap_data(user)

    # Fetching workout history
    workout_history = Workout.objects.filter(user=user)

    context = {
        "workout_history": workout_history,
        "current_goals": current_goals,
        "graph": graph,
        "daily_intake_ml": daily_intake_ml,
        "today_emotion": today_emotion,
        "heatmap_data_list": heatmap_data_list,
        "current_month_name": current_month_name,
    }

    return render(request, "homepage.html", context)

 
@login_required(login_url='/tracker/login/')
def user_profile(request):
    try:
        current_month = timezone.now().month

        # Filter the entries for the current user and the current month
        mental_health_entries = MentalHealth.objects.filter(user=request.user, date__month=current_month)

        # Aggregating data for display
        emotions = mental_health_entries.values("emotion").annotate(count=Count("emotion"))
        daily_gratitude = mental_health_entries.values("date", "daily_gratitude")
        self_care_habits = mental_health_entries.values("date", "self_care_habit")
        energy_levels = mental_health_entries.values("date", "energy_level")
        rants = mental_health_entries.values("date", "rant")

        # Generate charts
        emotion_chart = generate_emotion_chart(request.user)
        energy_level_chart = generate_energy_level_graph(request.user)

        context = {
            "emotions": emotions,
            "daily_gratitude": daily_gratitude,
            "self_care_habits": self_care_habits,
            "energy_levels": energy_levels,
            "rants": rants,
            "emotion_chart": emotion_chart,
            "energy_level_chart": energy_level_chart,
        }

        return render(request, "user_profile.html", context)
    
    except Exception as e:
        print(f"Error in user_profile views: {e}")
        return redirect("tracker:homepage")
    


@login_required(login_url='/tracker/login/')
def mental_health(request):
    if request.method == 'POST':
        form = MentalHealthForm(request.POST)
        if form.is_valid():
            mental_health_entry = form.save(commit=False)
            mental_health_entry.user = request.user
            mental_health_entry.save()
            return redirect('tracker:mental_health_summary')
    else:
        form = MentalHealthForm()
    
    return render(request, 'mental_health.html', {'form': form})


@login_required(login_url='/tracker/login/')
def mental_health_summary(request):
    try:
        current_month = timezone.now().month

        # Filter the entries for the current user and the current month
        mental_health_entries = MentalHealth.objects.filter(user=request.user, date__month=current_month)

        emotions = mental_health_entries.values("emotion").annotate(count=Count("emotion"))
        daily_gratitude = mental_health_entries.values("date", "daily_gratitude")
        self_care_habits = mental_health_entries.values("date", "self_care_habit")
        energy_levels = mental_health_entries.values("date", "energy_level")
        rants = mental_health_entries.values("date", "rant")

        # chart generations
        emotion_chart = generate_emotion_chart(request.user)
        energy_level_chart = generate_energy_level_graph(request.user)

        context = {
            "emotions": emotions,
            "daily_gratitude": daily_gratitude,
            "self_care_habits": self_care_habits,
            "energy_levels": energy_levels,
            "rants": rants,
            "emotion_chart": emotion_chart,
            "energy_level_chart": energy_level_chart,
            "mental_health_entries": mental_health_entries  
        }

        return render(request, "mental_health_summary.html", context)
    
    except Exception as e:
        print(f"Error in mental_health_summary views: {e}")
        return redirect("tracker:homepage")


@login_required(login_url='/tracker/login/')
def new_goal(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        description = request.POST.get("description")
        if description:
            print(f"Request user: {request.user} (Type: {type(request.user)})")
            print(f"Request user ID: {request.user.id}")

            try:
                # Retrieve the user instance
                user = User.objects.get(id=request.user.id)
                print(f"Retrieved user: {user} (Type: {type(user)})")

                # Create the goal
                Goal.objects.create(user=user, description=description)
            except User.DoesNotExist:
                print("User does not exist")
            except Exception as e:
                print(f"Unexpected error: {e}")

    return redirect("tracker:index")


@login_required(login_url='/tracker/login/')
def toggle_goal(request, goal_id):
    if request.method == "POST" and request.is_ajax():
        try:
            goal = Goal.objects.filter(pk=goal_id, user=request.user)
            goal.achieved = not goal.achieved
            goal.save()
            return JsonResponse({"success": True})
        except Goal.DoesNotExist:
            return JsonResponse({"success": False, "error": "Goal not found."})
    return JsonResponse({"success": False, "error": "Invalid request."})


@login_required(login_url='/tracker/login/')
def edit_goal(request, goal_id):
    if request.method == "POST" and request.is_ajax():
        try:
            goal = Goal.objects.get(pk=goal_id, user=request.user)
            new_description = json.loads(request.body).get("description")
            goal.description = new_description
            goal.save()
            return JsonResponse({"success": True})
        except Goal.DoesNotExist:
            return JsonResponse({"success": False, "error": "Goal not found."})
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required(login_url='/tracker/login/')
def delete_goal(request, goal_id):
    if request.method == "POST" and request.is_ajax():
        try:
            goal = Goal.objects.get(pk=goal_id, user=request.user)
            goal.delete()
            return JsonResponse({"success": True})
        except Goal.DoesNotExist:
             return JsonResponse({"success": False, "error": "Goal not found."})
    return JsonResponse({"success": False, "error": "Invalid request"})


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


@login_required(login_url='/tracker/login/')
def log_workout(request):
    if request.method == "POST":
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.calories_burned = calculated_calories_burned(workout.activity_type, workout.duration_minutes)
            workout.save()
            return redirect("tracker:index")
    else:
        form = WorkoutForm()
    return render(request, "log_workout.html", {"form": form})


@login_required(login_url='/tracker/login/')
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id) 
    if request.method == "POST":
        workout.delete()
        return redirect("index")
    return redirect("tracker:user_profile")    


@login_required(login_url='/tracker/login/')
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    if request.method == "POST":
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        form = WorkoutForm(instance=workout)
    return render(request, "edit_workout.html", {"form": form})



@login_required(login_url='/tracker/login/')
def water_intake(request):
    if request.method == "POST":
        form = WaterIntakeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = WaterIntakeForm()
        return render(request, "water_intake.html", {"form": form})
    


           