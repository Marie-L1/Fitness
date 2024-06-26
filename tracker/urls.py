from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path("", views.index, name="index"),
    path("homepage/", views.homepage, name="homepage"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("new_goal/", views.new_goal, name="new_goal"),
    path("edit_goal/<int:goal_id>/", views.edit_goal, name="edit_goal"),
    path("delete_goal/<int:goal_id>/", views.delete_goal, name="delete_goal"),
    path("user_profile/", views.user_profile, name="user_profile"),
    path("edit_workout/<int:workout_id>", views.edit_workout, name="edit_workout"),
    path("delete_workout/<int:workout_id>", views.delete_workout, name="edit_workout"),
    path("mental_health/", views.mental_health, name="mental_health"),
    path("mental_health_summary/", views.mental_health_summary, name="mental_health_summary"),
    path("edit_mental_health_log/", views.mental_health, name="edit_mental_health_log"),
    path("delete_mental_health_log", views.mental_health, name="delete_mental_health_log"),
    path("log_workout/", views.log_workout, name="log_workout"),
    path("water_intake/", views.water_intake, name="water_intake")
]