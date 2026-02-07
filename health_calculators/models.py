"""
Models for tracking health metrics over time.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class BMILog(models.Model):
    """Track BMI changes over time"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bmi_logs')
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Weight in kg"))
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Height in cm"))
    bmi = models.DecimalField(max_digits=4, decimal_places=2)
    category = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - BMI {self.bmi} on {self.date}"

class NutritionLog(models.Model):
    """Simple daily nutrition tracker"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_logs')
    date = models.DateField(auto_now_add=True)
    item_name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=1, default=0, help_text=_("Protein in grams"))
    carbs = models.DecimalField(max_digits=5, decimal_places=1, default=0, help_text=_("Carbs in grams"))
    fats = models.DecimalField(max_digits=5, decimal_places=1, default=0, help_text=_("Fats in grams"))
    
    MEAL_CHOICES = [
        ('breakfast', _('Breakfast')),
        ('lunch', _('Lunch')),
        ('dinner', _('Dinner')),
        ('snack', _('Snack')),
    ]
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, default='snack')

    class Meta:
        ordering = ['-date', 'meal_type']

    def __str__(self):
        return f"{self.item_name} ({self.calories} kcal)"