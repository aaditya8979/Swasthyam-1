from django.contrib import admin
from .models import BMILog, NutritionLog

@admin.register(BMILog)
class BMILogAdmin(admin.ModelAdmin):
    list_display = ('user', 'bmi', 'category', 'date')
    list_filter = ('category', 'date')

@admin.register(NutritionLog)
class NutritionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_name', 'calories', 'meal_type', 'date')
    list_filter = ('meal_type', 'date')