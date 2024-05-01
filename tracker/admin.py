from django.contrib import admin
from .models import User,Workout, Goal, WaterIntake


# Register your models here.
admin.site.register(User)
admin.site.register(Workout)
admin.site.register(Goal)
admin.site.register(WaterIntake)
