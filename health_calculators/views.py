from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from datetime import timedelta, date
from .forms import BMICalculatorForm, DueDateForm, OvulationForm, NutritionForm, PregnancyWeightForm
from .models import BMILog, NutritionLog
from django.db.models import Sum

@login_required
def calculators_home(request):
    """Dashboard for all health tools"""
    return render(request, 'calculators/home.html')

@login_required
def bmi_calculator(request):
    result = None
    form = BMICalculatorForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        h = form.cleaned_data['height'] / 100  # cm to meters
        w = form.cleaned_data['weight']
        bmi = round(w / (h ** 2), 2)
        
        # Determine category
        if bmi < 18.5: category = 'Underweight'
        elif 18.5 <= bmi < 25: category = 'Normal weight'
        elif 25 <= bmi < 30: category = 'Overweight'
        else: category = 'Obese'
        
        result = {'bmi': bmi, 'category': category}
        
        # Save to history
        BMILog.objects.create(
            user=request.user, height=form.cleaned_data['height'],
            weight=w, bmi=bmi, category=category
        )
    
    # Get history
    history = BMILog.objects.filter(user=request.user).order_by('-date')[:5]
    
    return render(request, 'calculators/bmi.html', {'form': form, 'result': result, 'history': history})

@login_required
def due_date_calculator(request):
    result = None
    form = DueDateForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        lmp = form.cleaned_data['last_period_date']
        cycle = form.cleaned_data['cycle_length']
        
        # Naegele's Rule adjustment
        # EDD = LMP + 280 days + (CycleLength - 28) days
        edd = lmp + timedelta(days=280 + (cycle - 28))
        
        result = {
            'edd': edd,
            'conception': lmp + timedelta(days=14 + (cycle - 28)),
            'trimester_1_end': lmp + timedelta(weeks=12),
            'trimester_2_end': lmp + timedelta(weeks=26),
        }
        
    return render(request, 'calculators/due_date.html', {'form': form, 'result': result})

@login_required
def ovulation_calculator(request):
    result = None
    form = OvulationForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        lmp = form.cleaned_data['last_period_date']
        cycle = form.cleaned_data['cycle_length']
        
        # Ovulation is approx 14 days before NEXT period
        next_period = lmp + timedelta(days=cycle)
        ovulation = next_period - timedelta(days=14)
        
        fertile_window_start = ovulation - timedelta(days=5)
        fertile_window_end = ovulation + timedelta(days=1)
        
        result = {
            'ovulation': ovulation,
            'fertile_start': fertile_window_start,
            'fertile_end': fertile_window_end,
            'next_period': next_period
        }
        
    return render(request, 'calculators/ovulation.html', {'form': form, 'result': result})

@login_required
def pregnancy_weight_calculator(request):
    result = None
    form = PregnancyWeightForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        pre_w = form.cleaned_data['pre_pregnancy_weight']
        curr_w = form.cleaned_data['current_weight']
        h = form.cleaned_data['height'] / 100
        week = form.cleaned_data['week']
        
        bmi = pre_w / (h ** 2)
        gained = curr_w - pre_w
        
        # IOM Guidelines (Simplified)
        if bmi < 18.5: min_g, max_g = 12.5, 18
        elif bmi < 25: min_g, max_g = 11.5, 16
        elif bmi < 30: min_g, max_g = 7, 11.5
        else: min_g, max_g = 5, 9
        
        # Expected gain at current week (rough estimate)
        expected_min = (min_g / 40) * week
        expected_max = (max_g / 40) * week
        
        status = "On Track"
        if gained < expected_min: status = "Below Recommended"
        elif gained > expected_max: status = "Above Recommended"
        
        result = {
            'gained': round(gained, 1),
            'recommended_range': f"{round(expected_min, 1)} - {round(expected_max, 1)} kg",
            'status': status,
            'total_target': f"{min_g} - {max_g} kg"
        }
        
    return render(request, 'calculators/pregnancy_weight.html', {'form': form, 'result': result})

@login_required
def nutrition_tracker(request):
    today = date.today()
    logs = NutritionLog.objects.filter(user=request.user, date=today)
    
    # Calculate totals
    totals = logs.aggregate(
        cal=Sum('calories'),
        prot=Sum('protein'),
        carb=Sum('carbs'),
        fat=Sum('fats')
    )
    
    if request.method == 'POST':
        form = NutritionForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            messages.success(request, 'Meal added successfully!')
            return redirect('health_calculators:nutrition')
    else:
        form = NutritionForm()
        
    context = {
        'form': form,
        'logs': logs,
        'totals': totals,
        'today': today
    }
    return render(request, 'calculators/nutrition.html', context)