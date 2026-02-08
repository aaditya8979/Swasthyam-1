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
    context = {}

    if request.method == "POST":
        pre_weight = float(request.POST.get("pre_weight"))
        current_weight = float(request.POST.get("current_weight"))
        week = int(request.POST.get("week"))

        weight_gain = round(current_weight - pre_weight, 2)

        if weight_gain < 0:
            message = "Weight loss during pregnancy should be discussed with a doctor."
        elif weight_gain <= (week * 0.5):
            message = "Your weight gain is within a healthy range."
        else:
            message = "Your weight gain is higher than expected. Consider consulting a doctor."

        context.update({
            "weight_gain": weight_gain,
            "message": message
        })

    return render(request, "calculators/pregnancy_weight.html", context)

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