from django.contrib import admin
from .models import User,Workout, Goal, WaterIntake, MentalHealth


# Register your models here.
admin.site.register(User)
admin.site.register(Workout)
admin.site.register(Goal)
admin.site.register(WaterIntake)
admin.site.register(MentalHealth)
