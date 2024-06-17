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

@login_required(login_url='/tracker/login/')
def homepage(request):
    user = request.user
    print(f"User: {user}, ID: {user.id}")   # Debugging

    today = datetime.now().date()
    current_month = datetime.now().month
    current_month_name = datetime.now().strftime('%B')

    # Fetching current goals (if any)
    current_goals = Goal.objects.filter(user=user, achieved=False)

    # Fetching daily water intake
    daily_intake = WaterIntake.objects.filter(user=user, date=today)
    daily_intake_ml = daily_intake.aggregate(total_intake=Sum("amount_ml"))["total_intake"] or 0

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

    # Fetching daily emotion logged for today
    today_emotion_entry = MentalHealth.objects.filter(user=user, date=today).first()
    today_emotion = today_emotion_entry.emotion if today_emotion_entry else None

    # Generating heatmap data for the current month
    logged_dates = WaterIntake.objects.filter(user=user, date__month=current_month).dates("date", "day")
    heatmap_data = {date.day: 0 for date in logged_dates}
    for date in logged_dates:
        day = date.day
        heatmap_data[day] += 1

    # Normalize heatmap data for color intensity
    max_intensity = max(heatmap_data.values(), default=1)
    heatmap_data_list = [{'day': day, 'color_value': heatmap_data[day] / max_intensity} for day in range(1, today.day + 1)]

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

    return render(request, "tracker/homepage.html", context)


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
def user_profile(request):
    try:
        # get current user
        user = request.User
        print(f"User: {user}, ID: {user.id}")   # debugging

        past_workouts = Workout.objects.filter(user=user).order_by("-date")

        # get current month's emotions and prepare data for the pie chart
        current_month = timezone.now().month
        emotions = MentalHealth.objects.filter(user=user, date__month=current_month)
        emotion_counts = emotions.values("entry").annotate(count=Count("entry"))

        # Prepare data for the emotions pie chart
        emotion_data = {entry["entry"]: entry["count"] for entry in emotion_counts}
        labels = list(emotion_data.keys())
        sizes = list(emotion_data.values())
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
        ax1.axis("equal")  # Equal ratio so the pie chart is a circle

        # Save the emotions pie chart to a png image
        buffer1 = BytesIO()
        plt.savefig(buffer1, format="png")
        plt.close(fig1)
        buffer1.seek(0)
        emotion_chart = base64.b64encode(buffer1.getvalue()).decode("utf-8")
        buffer1.close()

        # get monthly water intake data and prepare for the graph
        water_intake = WaterIntake.objects.filter(user=user, date__month=current_month)
        daily_water_intake = water_intake.values("date").annotate(total_amount=Count("amount_ml").order_by("date"))

        dates = [entry["date"] for entry in daily_water_intake]
        amounts = [entry["total_amount"] for entry in daily_water_intake]

        fig2, ax2 = plt.subplots()
        ax2.plot(dates, amounts, marker="o")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Monthly Water Intake")
        plt.xticks(rotation=45)

        # Save the water intake graph to a png image
        buffer2 = BytesIO()
        plt.savefig(buffer2, format="png")
        plt.close(fig2)
        buffer2.seek(0)
        water_intake_chart = base64.b64encode(buffer2.getvalue()).decode("utf-8")
        buffer2.close()

        context = {
            "user": user,
            "past_workouts": past_workouts,
            "emotion_chart": emotion_chart,
            "water_intake_chart": water_intake_chart,
        }

        return render(request, "user_profile.html", context)
    
    except Exception as e:
        print(f"Error in user_profile views : {e}")
        return redirect("tracker:index")



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
    

@login_required(login_url='/tracker/login/')
def mental_health(request):
    if request.method == "POST":
        form = MentalHealthForm(request.POST)
        if form.is_valid():
            mental_health_entry = form.save(commit=False)
            mental_health_entry.user = request.user
            mental_health_entry.save()
            return redirect("tracker:mental_health_summary")
    else:
        form = MentalHealthForm()
        
    return render(request, "mental_health.html", {"form": form})

           


@login_required(login_url='/tracker/login/')
def mental_health_summary(request):
    current_month = timezone.now().month

    #filter the entries for the current user and the current month
    mental_health_entries = MentalHealth.objects.filter(user=request.user, date__month=current_month)

    # get data for each field
    emotions = mental_health_entries("emotion").annotate(count=Count("emotion"))
    daily_gratitude = mental_health_entries("date", "daily_graitiude")
    self_care_habits = mental_health_entries("date", "self_care_habit")
    energy_levels = mental_health_entries("date", "energy_level")
    rants = mental_health_entries("date", "rant")

    # data for pie chart and graph
    emotion_labels = [entry["emotion"] for entry in emotions]
    emotion_sizes = [entry["count"] for entry in emotions]

    fig1, ax1 = plt.subplots()
    ax1.pie(emotion_sizes, lables=emotion_labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")

    # save pie chart to png image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    emotion_chart = base64.b64encoded(buffer.getvalue()).decode("utf-8")
    buffer.close()

    # create the line graph for energy levels
    dates = [entry["date"] for entry in energy_levels]
    levels = [entry["energy_level"] for entry in energy_levels]

    plt.figure()
    plt.plot(dates, levels)
    plt.xlabel("Date")
    plt.ylabel("Daily Energy Level")
    plt.grid(True)

    # Save the line graph to png image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    energy_level_chart = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return render(request, "mental_health_summary.html", {
        "emotions": emotions,
        "daily_gratitude": daily_gratitude,
        "self_care_habits": self_care_habits,
        "energy_levels": energy_levels,
        "rants": rants,
        "emotion_chart": emotion_chart,
        "energy_level_chart": energy_level_chart
    })