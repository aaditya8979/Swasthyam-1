from django import forms
from django.utils.translation import gettext_lazy as _
from .models import NutritionLog

class BMICalculatorForm(forms.Form):
    height = forms.FloatField(label=_("Height (cm)"), min_value=50, max_value=300, 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '170'}))
    weight = forms.FloatField(label=_("Weight (kg)"), min_value=10, max_value=500,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '70'}))

class DueDateForm(forms.Form):
    last_period_date = forms.DateField(
        label=_("First day of last period"),
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    cycle_length = forms.IntegerField(
        label=_("Average Cycle Length (days)"),
        initial=28, min_value=20, max_value=45,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )

class PregnancyWeightForm(forms.Form):
    pre_pregnancy_weight = forms.FloatField(label=_("Pre-pregnancy Weight (kg)"),
        widget=forms.NumberInput(attrs={'class': 'form-input'}))
    current_weight = forms.FloatField(label=_("Current Weight (kg)"),
        widget=forms.NumberInput(attrs={'class': 'form-input'}))
    height = forms.FloatField(label=_("Height (cm)"),
        widget=forms.NumberInput(attrs={'class': 'form-input'}))
    week = forms.IntegerField(label=_("Pregnancy Week"), min_value=1, max_value=42,
        widget=forms.NumberInput(attrs={'class': 'form-input'}))

class OvulationForm(forms.Form):
    last_period_date = forms.DateField(
        label=_("First day of last period"),
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    cycle_length = forms.IntegerField(
        label=_("Average Cycle Length"), initial=28, min_value=21, max_value=35,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )

class NutritionForm(forms.ModelForm):
    class Meta:
        model = NutritionLog
        fields = ['item_name', 'calories', 'protein', 'carbs', 'fats', 'meal_type']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Oatmeal'}),
            'calories': forms.NumberInput(attrs={'class': 'form-input'}),
            'protein': forms.NumberInput(attrs={'class': 'form-input'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-input'}),
            'fats': forms.NumberInput(attrs={'class': 'form-input'}),
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
        }