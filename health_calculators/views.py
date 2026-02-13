from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from datetime import timedelta, date
from .forms import BMICalculatorForm, DueDateForm, OvulationForm, NutritionForm
from .models import BMILog, NutritionLog
from django.db.models import Sum
from django.conf import settings
from openai import OpenAI
import json

# Initialize OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def calculators_home(request):
    return render(request, 'calculators/home.html')

@login_required
def bmi_calculator(request):
    result = None
    form = BMICalculatorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        h = form.cleaned_data['height'] / 100
        w = form.cleaned_data['weight']
        bmi = round(w / (h ** 2), 2)
        if bmi < 18.5: category = 'Underweight'
        elif 18.5 <= bmi < 25: category = 'Normal weight'
        elif 25 <= bmi < 30: category = 'Overweight'
        else: category = 'Obese'
        result = {'bmi': bmi, 'category': category}
        BMILog.objects.create(user=request.user, height=form.cleaned_data['height'], weight=w, bmi=bmi, category=category)
    history = BMILog.objects.filter(user=request.user).order_by('-date')[:5]
    return render(request, 'calculators/bmi.html', {'form': form, 'result': result, 'history': history})

@login_required
def due_date_calculator(request):
    result = None
    form = DueDateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        lmp = form.cleaned_data['last_period_date']
        cycle = form.cleaned_data['cycle_length']
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
        next_period = lmp + timedelta(days=cycle)
        ovulation = next_period - timedelta(days=14)
        result = {
            'ovulation': ovulation,
            'fertile_start': ovulation - timedelta(days=5),
            'fertile_end': ovulation + timedelta(days=1),
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
        if weight_gain < 0: message = "Weight loss should be discussed with a doctor."
        elif weight_gain <= (week * 0.5): message = "Weight gain is healthy."
        else: message = "Weight gain is higher than expected."
        context.update({"weight_gain": weight_gain, "message": message})
    return render(request, "calculators/pregnancy_weight.html", context)

# --- AI NUTRITION TRACKER ---
@login_required
def nutrition_tracker(request):
    today = date.today()
    logs = NutritionLog.objects.filter(user=request.user, date=today)
    totals = logs.aggregate(cal=Sum('calories'), prot=Sum('protein'), carb=Sum('carbs'), fat=Sum('fats'))
    
    ai_data = None

    if request.method == 'POST':
        if 'analyze_food' in request.POST:
            # AI ANALYSIS
            food_text = request.POST.get('food_text')
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Return JSON only: {'calories': int, 'protein': int, 'carbs': int, 'fats': int} for the food."},
                        {"role": "user", "content": f"Analyze: {food_text}"}
                    ]
                )
                ai_data = json.loads(response.choices[0].message.content)
                ai_data['food_name'] = food_text
            except:
                messages.error(request, "AI could not analyze that food. Try simpler text.")
        
        elif 'save_meal' in request.POST:
            # SAVE ANALYZED DATA
            NutritionLog.objects.create(
                user=request.user,
                food_name=request.POST.get('food_name'),
                calories=request.POST.get('calories'),
                protein=request.POST.get('protein'),
                carbs=request.POST.get('carbs'),
                fats=request.POST.get('fats'),
                date=today
            )
            messages.success(request, "Meal logged successfully!")
            return redirect('health_calculators:nutrition')

    return render(request, 'calculators/nutrition.html', {'logs': logs, 'totals': totals, 'ai_data': ai_data})