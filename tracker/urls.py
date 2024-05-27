from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("new_goal/", views.new_goal, name="new_goal"),
    path("profile/", views.user_profile, name="user_profile"),
    path("edit_workout/<int:workout_id>", views.edit_workout, name="edit_workout"),
    path("mental_health/", views.mental_health, name="mental_health"),
    path("mental_health_summary/", views.mental_health_summary, name="mental_health_summary")
]