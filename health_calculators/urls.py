"""
URL patterns for health calculators app.
"""

from django.urls import path
from . import views

app_name = 'health_calculators'

urlpatterns = [
    path('', views.calculators_home, name='home'),
    path('bmi/', views.bmi_calculator, name='bmi'),
    path('pregnancy-weight/', views.pregnancy_weight_calculator, name='pregnancy_weight'),
    path('due-date/', views.due_date_calculator, name='due_date'),
    path('ovulation/', views.ovulation_calculator, name='ovulation'),
    path('nutrition/', views.nutrition_tracker, name='nutrition'),

]
