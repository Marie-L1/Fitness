from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.db.models import Sum, Count, Avg
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpRequest
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
import matplotlib.pyplot as plt
import base64
from io import BytesIO
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
    user = User.objects.get(id=request.user)
    print(f"User: {user}, ID: {user.id}")   # debugging
    today = timezone.now().date()
    current_month = timezone.now().month
    current_month_name = calendar.month_name[current_month]

    # Goals
    current_goals = Goal.objects.filter(user=user, achieved=False)

    # water intake calculation 
    daily_intake = WaterIntake.objects.filter(user=user, date=today)
    daily_intake_ml = daily_intake.aggregate(total_intake=Sum("amount_ml"))["total_intake"] or 0
      
    # generate monthly graph
    monthly_intake = WaterIntake.objects.filter(user=user, date__year=today.year, date__month=current_month).values("date").annotate(total_intake=Sum("amount_ml"))
    dates = [entry["date"] for entry in monthly_intake]
    intake_values = [entry["total_intake"] for entry in monthly_intake]

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
    plt.close()

    # daily emotion logged for today
    today_emotion = Emotion.objects.filter(user=user, date=today).first()

    # monthly data log heatmap
    logged_dates = WaterIntake.objects.filter(user=user, date__month=current_month).dates("date", "day")
    logged_dates_set = set(logged_dates)

    # prepare data for heatmap
    heatmap_data = defaultdict(lambda: 0)
    for date in logged_dates:
        day = date.day
        heatmap_data[day] += 1

    # creat the heatmap data for the current month
        days_in_month = calendar.monthrange(today.year, current_month)[1]
        heatmap_data_list = [heatmap_data[day] for day in range(1, days_in_month + 1)]

    # calculate colour intensity values for heatmap
    max_intensity = max(heatmap_data.values(), default=1)
    for entry in heatmap_data_list:
        entry["color_value"] = np.interp(entry["color_value"], [0, max_intensity], [0, 1])

    # get workout history and current goals
    if request.user.is_authenticated:
        workout_history = Workout.objects.filter(user=request.user)
        current_goals= Goal.objects.filter(user=request.user, achieved=False)
    else:
        workout_history = None
        current_goals = None

    context = {
        "workout_history": workout_history,
        "current_goals": current_goals,
        "graph": graph,
        "daily_intake_ml": daily_intake_ml,
        "today_emotion": today_emotion,
        "heatmap_data_list": heatmap_data_list,
        "days_in_month": days_in_month,
        "current_month_name": current_month_name,
    }

    return render(request, "index.html", context)



def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        logger.debug("login attempt")
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            logger.debug("login successful")
            return HttpResponseRedirect(reverse("tracker:index"))
        else:
            logger.warning(f"Invalid username and/or password.")
            return render(request, "login.html", {"message": "Invalid username and/or password."})
    else:
        return render(request, "login.html")


@login_required(login_url='/tracker/login/')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            username = user.username
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                logger.debug(f"User {username} registered and logged in.")
                return HttpResponseRedirect(reverse("index"))
            else:
                logger.error("User could not be authenticated after registration.")
                return render(request, "register.html", {"form": form, "message": "User could not be authenticated."})
        else:
            logger.error(f"Form errors: {form.errors}")
            return render(request, "register.html", {"form": form, "message": form.errors})
    else:
        form = RegistrationForm()
    
    return render(request, "register.html", {"form": form})



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

    return redirect("index")


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
            return redirect("index")
    else:
        form = WorkoutForm()
    return render(request, "log_workout.html", {"form": form})


@login_required(login_url='/tracker/login/')
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id) 
    if request.method == "POST":
        workout.delete()
        return redirect("index")
    return redirect("user_profile")    


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
       form = MentalHealthForm
    return render(request, "tracker/mental_health.html", {"form": form})
           


@login_required(login_url='/tracker/login/')
def mental_health_summary(request):
    emotions = Emotion.objects.filter(user=request.user, date__month=timezone.now().month)
    daily_gratitude = DailyGratitude.objects.filter(user=request.user, date__month=timezone.now().month)
    self_care_habits = SelfCareHabit.objects.filter(user=request.user, date__month=timezone.now().month)
    energy_levels = EnergyLevel.objects.filter(user=request.user, date__month=timezone.now().month)
    rants = Rant.objects.filter(user=request.user, date__month=timezone.now().month)

    # data for pie chart and graph
    emotion_counts = emotions.values("emotion").annotate(count=Count("emotion"))
    avg_energy_level = energy_levels.aggregate(avg_level=Avg("energy_level"))["avg_level"]

    # generate pie chart for emotions
    labels = [entry["emotion"] for entry in emotion_counts]
    sizes = [entry["count"] for entry in emotion_counts]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, lables=labels, autopct="%1.1f%%", startangle=90)
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
        "emotion_counts": emotion_counts,
        "avg_energy_level": avg_energy_level,
        "emotion_chart": emotion_chart,
        "energy_level_chart": energy_level_chart
    })