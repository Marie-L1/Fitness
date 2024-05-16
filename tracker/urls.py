from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_goal/", views.new_goal, name="new_goal"),
    path("profile/", views.user_profile, name="user_profile"),
    path("edit_workout/<int:workout_id>", views.edit_workout, name="edit_workout"),
    path("mental_health/", views.mental_heatlh, name="mental_health")
]