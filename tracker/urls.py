from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_goal/", views.new_goal, name="new_goal"),
    path("profile/", views.user_profile, name="user_profile")
]