"""
Maternal Health RAG Chatbot - Context-Aware AI Assistant.
Uses OpenAI API with user profile data for personalized responses.
ENHANCED with Medical Records Vault for document management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q, Count
from users.models import ChatHistory
from .models import MedicalRecord, UltrasoundImage, AppointmentReminder
from .forms import MedicalRecordForm, UltrasoundDetailsForm, AppointmentForm
from openai import OpenAI
import json
from datetime import datetime, date, timedelta

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


@login_required
def maternal_home_view(request):
    """
    Maternal health landing page with overview stats.
    """
    profile = request.user.profile
    recent_chats = request.user.chat_history.order_by('-created_at')[:5]
    
    # Medical Records Stats
    total_records = request.user.medical_records.count()
    ultrasound_count = request.user.medical_records.filter(record_type='ultrasound').count()
    recent_records = request.user.medical_records.all()[:3]
    
    # Upcoming Appointments
    upcoming_appointments = request.user.appointments.filter(
        appointment_date__gte=date.today(),
        is_completed=False
    ).order_by('appointment_date')[:3]
    
    context = {
        'profile': profile,
        'recent_chats': recent_chats,
        'total_records': total_records,
        'ultrasound_count': ultrasound_count,
        'recent_records': recent_records,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'maternal/home.html', context)


@login_required
def chat_view(request):
    """
    Main RAG chatbot interface.
    """
    profile = request.user.profile
    chat_history = request.user.chat_history.order_by('-created_at')[:20]
    
    context = {
        'profile': profile,
        'chat_history': list(reversed(chat_history)),  # Oldest first
    }
    return render(request, 'maternal/chat.html', context)


@login_required
@require_http_methods(["POST"])
def chat_api(request):
    """
    AJAX endpoint for chatbot responses.
    Constructs context-aware prompts using user profile.
    Falls back to intelligent pre-programmed responses if OpenAI unavailable.
    """
    try:
        data = json.loads(request.body)
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return JsonResponse({
                'success': False,
                'error': _('Please enter a question.')
            }, status=400)
        
        # Get user profile for context
        profile = request.user.profile
        
        # Try OpenAI API first
        ai_answer = None
        used_openai = False
        
        # 1. Try OpenAI Generation
        if settings.OPENAI_API_KEY:
            try:
                # Build context-aware system prompt
                system_prompt = build_system_prompt(profile)
                
                # Call OpenAI API (NEW SYNTAX)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use 3.5-turbo for speed/cost, or gpt-4
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_question}
                    ],
                    temperature=0.7,
                    max_tokens=400,
                )
                
                ai_answer = response.choices[0].message.content.strip()
                used_openai = True
                
            except Exception as e:
                print(f"OpenAI API Error: {e}") # Log error to terminal
                ai_answer = None # Mark as failed so we use fallback
        
        # 2. Fallback to Intelligent Response (if OpenAI failed or no key)
        if not ai_answer:
            print("Using Intelligent Fallback Response")
            ai_answer = get_intelligent_response(user_question, profile)
        
        # 3. Final Safety Net (if even fallback returns nothing)
        if not ai_answer:
            ai_answer = "I'm here to help, but I didn't quite understand that. You can ask me about pregnancy symptoms, diet, appointments, or check your medical vault."

        # Save to chat history
        chat_record = ChatHistory.objects.create(
            user=request.user,
            question=user_question,
            answer=ai_answer,
            user_age_at_time=profile.age or 0,
            pregnancy_weeks_at_time=profile.pregnancy_weeks or 0,
        )
        
        return JsonResponse({
            'success': True,
            'answer': ai_answer,
            'chat_id': chat_record.id,
            'timestamp': chat_record.created_at.isoformat(),
            'used_ai': used_openai
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        print(f"Chat API Critical Error: {e}") # This will show you exactly what broke
        return JsonResponse({
            'success': False,
            'error': 'An internal error occurred. Please try again.'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def rate_chat(request):
    """
    Allow users to rate chatbot responses as helpful or not.
    """
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        helpful = data.get('helpful')  # True or False
        
        chat = ChatHistory.objects.get(id=chat_id, user=request.user)
        chat.helpful = helpful
        chat.save()
        
        return JsonResponse({
            'success': True,
            'message': _('Thank you for your feedback!')
        })
        
    except ChatHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Chat not found.')
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def chat_history_view(request):
    """
    View all past chat conversations.
    """
    chats = request.user.chat_history.order_by('-created_at')
    
    # Group by date
    from itertools import groupby
    
    grouped_chats = {}
    for key, group in groupby(chats, lambda x: x.created_at.date()):
        grouped_chats[key] = list(group)
    
    context = {
        'grouped_chats': grouped_chats,
    }
    return render(request, 'maternal/chat_history.html', context)


# ============================================================================
# MEDICAL RECORDS VAULT - NEW FEATURE
# ============================================================================

@login_required
def medical_vault_view(request):
    """
    Main medical records vault - organized by trimester.
    """
    profile = request.user.profile
    
    # Get all records
    all_records = request.user.medical_records.filter(is_archived=False)
    
    # Filter by type if specified
    filter_type = request.GET.get('type', 'all')
    if filter_type != 'all':
        all_records = all_records.filter(record_type=filter_type)
    
    # Filter by trimester if specified
    filter_trimester = request.GET.get('trimester', 'all')
    if filter_trimester != 'all':
        all_records = all_records.filter(trimester=int(filter_trimester))
    
    # Organize by trimester
    trimester_1_records = request.user.medical_records.filter(trimester=1, is_archived=False)
    trimester_2_records = request.user.medical_records.filter(trimester=2, is_archived=False)
    trimester_3_records = request.user.medical_records.filter(trimester=3, is_archived=False)
    other_records = request.user.medical_records.filter(trimester=0, is_archived=False)
    
    # Statistics
    stats = {
        'total': all_records.count(),
        'ultrasounds': request.user.medical_records.filter(record_type='ultrasound').count(),
        'blood_tests': request.user.medical_records.filter(record_type='blood_test').count(),
        'prescriptions': request.user.medical_records.filter(record_type='prescription').count(),
        'important': request.user.medical_records.filter(is_important=True).count(),
    }
    
    # Recent uploads
    recent_uploads = all_records[:5]
    
    context = {
        'profile': profile,
        'all_records': all_records,
        'trimester_1_records': trimester_1_records,
        'trimester_2_records': trimester_2_records,
        'trimester_3_records': trimester_3_records,
        'other_records': other_records,
        'stats': stats,
        'recent_uploads': recent_uploads,
        'filter_type': filter_type,
        'filter_trimester': filter_trimester,
    }
    return render(request, 'maternal/medical_vault.html', context)


@login_required
def upload_medical_record(request):
    """
    Upload a new medical record.
    """
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            
            # Auto-detect trimester from pregnancy week if not set
            if record.pregnancy_week and not record.trimester:
                if record.pregnancy_week <= 13:
                    record.trimester = 1
                elif record.pregnancy_week <= 26:
                    record.trimester = 2
                else:
                    record.trimester = 3
            
            record.save()
            messages.success(request, _('Medical record uploaded successfully! 📄'))
            
            # If it's an ultrasound, offer to add details
            if record.record_type == 'ultrasound':
                return redirect('maternal_health:add_ultrasound_details', record_id=record.id)
            
            return redirect('maternal_health:medical_vault')
    else:
        form = MedicalRecordForm()
    
    context = {
        'form': form,
        'title': _('Upload Medical Record'),
    }
    return render(request, 'maternal/upload_record.html', context)


@login_required
def record_detail_view(request, record_id):
    """
    View detailed information about a medical record.
    """
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)
    
    # Get ultrasound details if available
    ultrasound_details = None
    if hasattr(record, 'ultrasound_details'):
        ultrasound_details = record.ultrasound_details
    
    context = {
        'record': record,
        'ultrasound_details': ultrasound_details,
    }
    return render(request, 'maternal/record_detail.html', context)


@login_required
def add_ultrasound_details(request, record_id):
    """
    Add detailed information for ultrasound images.
    """
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)
    
    if record.record_type != 'ultrasound':
        messages.error(request, _('This record is not an ultrasound.'))
        return redirect('maternal_health:record_detail', record_id=record.id)
    
    if request.method == 'POST':
        form = UltrasoundDetailsForm(request.POST)
        if form.is_valid():
            details = form.save(commit=False)
            details.medical_record = record
            details.save()
            messages.success(request, _('Ultrasound details added successfully!'))
            return redirect('maternal_health:record_detail', record_id=record.id)
    else:
        form = UltrasoundDetailsForm()
    
    context = {
        'form': form,
        'record': record,
    }
    return render(request, 'maternal/add_ultrasound_details.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_important_record(request, record_id):
    """
    AJAX endpoint to star/unstar important records.
    """
    try:
        record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)
        record.is_important = not record.is_important
        record.save()
        
        return JsonResponse({
            'success': True,
            'is_important': record.is_important,
            'message': _('Marked as important!') if record.is_important else _('Unmarked.')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def delete_medical_record(request, record_id):
    """
    Delete a medical record.
    """
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, _('Medical record deleted.'))
        return redirect('maternal_health:medical_vault')
    
    context = {
        'record': record,
    }
    return render(request, 'maternal/confirm_delete_record.html', context)


# ============================================================================
# APPOINTMENT MANAGEMENT
# ============================================================================

@login_required
def appointments_view(request):
    """
    View all appointments (upcoming and past).
    """
    upcoming = request.user.appointments.filter(
        appointment_date__gte=date.today(),
        is_completed=False
    ).order_by('appointment_date')
    
    past = request.user.appointments.filter(
        Q(appointment_date__lt=date.today()) | Q(is_completed=True)
    ).order_by('-appointment_date')[:10]
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    }
    return render(request, 'maternal/appointments.html', context)


@login_required
def add_appointment(request):
    """
    Schedule a new appointment.
    """
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, _('Appointment scheduled successfully! 📅'))
            return redirect('maternal_health:appointments')
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
    }
    return render(request, 'maternal/add_appointment.html', context)


@login_required
@require_http_methods(["POST"])
def mark_appointment_complete(request, appointment_id):
    """
    Mark appointment as completed.
    """
    try:
        appointment = get_object_or_404(AppointmentReminder, id=appointment_id, user=request.user)
        appointment.is_completed = True
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': _('Appointment marked as completed!')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_system_prompt(profile):
    """
    Construct a detailed system prompt with user context.
    This is the KEY to context-aware AI responses.
    """
    
    # Base prompt
    prompt = """You are a knowledgeable and empathetic maternal health assistant for Swasthyam, 
    a health companion platform. Your role is to provide accurate, supportive, and personalized 
    health information while ALWAYS reminding users to consult healthcare professionals for 
    medical decisions.
    
    IMPORTANT GUIDELINES:
    1. Always be supportive and empathetic
    2. Provide evidence-based information
    3. Never diagnose or prescribe medications
    4. Always recommend consulting healthcare providers for specific medical concerns
    5. Be culturally sensitive (many users are from India)
    6. Use simple, clear language
    7. Focus on maternal and child health topics
    
    """
    
    # Add user-specific context
    if profile.age:
        prompt += f"\nThe user is {profile.age} years old."
    
    if profile.pregnancy_status == 'pregnant' and profile.pregnancy_weeks:
        trimester = profile.pregnancy_trimester
        prompt += f"\nThe user is currently pregnant, in week {profile.pregnancy_weeks} (trimester {trimester})."
        
        if profile.due_date:
            days_until = (profile.due_date - datetime.now().date()).days
            if days_until > 0:
                prompt += f"\nTheir due date is in approximately {days_until} days."
    
    elif profile.pregnancy_status == 'postpartum':
        prompt += "\nThe user recently gave birth and is in the postpartum period."
    
    if profile.number_of_children > 0:
        prompt += f"\nThe user has {profile.number_of_children} {'child' if profile.number_of_children == 1 else 'children'}."
    
    if profile.bmi:
        bmi_category = profile.bmi_category
        prompt += f"\nThe user's current BMI is {profile.bmi} ({bmi_category})."
    
    prompt += "\n\nBased on this context, provide personalized yet general health guidance. "
    prompt += "Always end responses by encouraging users to discuss specific concerns with their healthcare provider."
    
    return prompt


def get_maternal_resources():
    """
    Curated list of reliable maternal health resources.
    These can be included in chatbot responses.
    """
    return {
        'emergency': {
            'title': _('Emergency Hotlines'),
            'content': [
                _('National Health Helpline (India): 1800-180-1104'),
                _('Women\'s Helpline: 181'),
                _('Ambulance: 108/102'),
            ]
        },
        'nutrition': {
            'title': _('Pregnancy Nutrition'),
            'content': [
                _('Eat iron-rich foods (spinach, lentils, beans)'),
                _('Get adequate folic acid (leafy greens, fortified cereals)'),
                _('Stay hydrated (8-10 glasses of water daily)'),
                _('Avoid raw/undercooked meat and unpasteurized dairy'),
            ]
        },
        'exercise': {
            'title': _('Safe Exercise During Pregnancy'),
            'content': [
                _('Walking (30 minutes daily)'),
                _('Prenatal yoga'),
                _('Swimming'),
                _('Avoid contact sports and activities with fall risk'),
            ]
        },
        'warning_signs': {
            'title': _('When to Call Your Doctor Immediately'),
            'content': [
                _('Severe abdominal pain'),
                _('Heavy vaginal bleeding'),
                _('Severe headache with vision changes'),
                _('Decreased fetal movement'),
                _('High fever (>101°F)'),
                _('Painful urination'),
            ]
        }
    }


def get_intelligent_response(question, profile):
    """
    Intelligent fallback response system with context awareness.
    Handles common queries when OpenAI API is unavailable.
    """
    
    question_lower = question.lower().strip()
    
    # Build personalized greeting prefix based on user context
    context_prefix = ""
    if profile.pregnancy_status == 'pregnant' and profile.pregnancy_weeks:
        trimester = profile.pregnancy_trimester
        context_prefix = f"As you're in week {profile.pregnancy_weeks} (trimester {trimester}), "
    
    # ============================================================================
    # GREETINGS & CASUAL CONVERSATION
    # ============================================================================
    
    greetings = ['hi', 'hello', 'hey', 'hii', 'hiii', 'helloo', 'good morning', 'good afternoon', 'good evening']
    if any(question_lower == greeting or question_lower.startswith(greeting + ' ') for greeting in greetings):
        responses = [
            f"Hello {profile.user.first_name or profile.user.username}! 👋 I'm your maternal health assistant. {context_prefix}I'm here to help answer your pregnancy and health questions. What would you like to know today?",
            f"Hi there! 😊 Great to see you. {context_prefix}How can I assist you with your maternal health journey today?",
            f"Hello! Welcome back. {context_prefix}I'm here to provide guidance on pregnancy, nutrition, baby care, and more. What's on your mind?"
        ]
        import random
        return random.choice(responses)
    
    # How are you variations
    if any(phrase in question_lower for phrase in ['how are you', 'how r u', 'how are u', 'sup', 'whats up', "what's up"]):
        return f"I'm here and ready to help you! 😊 More importantly, how are YOU feeling today? {context_prefix}I'd love to hear about your health and answer any questions you might have."
    
    # Thank you responses
    if any(phrase in question_lower for phrase in ['thank', 'thanks', 'thankyou', 'thank you', 'thx']):
        return "You're very welcome! 🙏 I'm always here whenever you need health guidance or support. Take care of yourself and your baby! Remember to consult your doctor for any specific concerns."
    
    # Goodbye responses
    if any(phrase in question_lower for phrase in ['bye', 'goodbye', 'see you', 'good night', 'goodnight']):
        return "Take care! 👋 Stay healthy and don't hesitate to come back anytime you have questions. Wishing you and your baby all the best!"
    
    # ============================================================================
    # PREGNANCY-SPECIFIC QUERIES
    # ============================================================================
    
    # Due date questions
    if any(phrase in question_lower for phrase in ['due date', 'when will', 'when is baby', 'delivery date']):
        if profile.due_date:
            days_until = (profile.due_date - date.today()).days
            if days_until > 0:
                return f"Based on your profile, your due date is {profile.due_date.strftime('%B %d, %Y')} - that's approximately {days_until} days from now! 📅 Remember, only about 5% of babies arrive exactly on their due date. Your baby will come when they're ready! Keep attending your regular checkups."
            else:
                return f"Your due date has passed! If you haven't delivered yet, please contact your doctor immediately. They may want to schedule an induction or monitor you closely. 🏥"
        else:
            return "I don't see a due date in your profile. You can add it in your profile settings to get personalized timeline information. Generally, pregnancy lasts about 40 weeks from your last menstrual period."
    
    # Trimester questions
    if any(phrase in question_lower for phrase in ['what trimester', 'which trimester', 'trimester am i']):
        if profile.pregnancy_status == 'pregnant' and profile.pregnancy_weeks:
            trimester = profile.pregnancy_trimester
            trimester_names = {1: "first", 2: "second", 3: "third"}
            return f"You're currently in your {trimester_names[trimester]} trimester! You're at week {profile.pregnancy_weeks}. 🤰\n\nTrimester {trimester} highlights:\n" + get_trimester_info(trimester)
        return "Please update your pregnancy status and current week in your profile to get personalized trimester information!"
    
    # Nutrition questions
    if any(phrase in question_lower for phrase in ['what to eat', 'nutrition', 'diet', 'food', 'eat', 'hungry']):
        nutrition_advice = """Here's nutrition guidance for a healthy pregnancy:
        
🥬 **Essential Foods:**
- Iron-rich foods: Spinach, lentils, beans, red meat
- Folic acid: Leafy greens, fortified cereals, citrus fruits
- Calcium: Milk, yogurt, cheese, fortified plant milk
- Protein: Eggs, fish (low mercury), chicken, tofu, legumes
- Omega-3: Walnuts, flaxseeds, fatty fish (salmon)

💧 **Hydration:** Drink 8-10 glasses of water daily

🚫 **Avoid:**
- Raw/undercooked meat, eggs, seafood
- Unpasteurized dairy products
- High-mercury fish (shark, swordfish)
- Excessive caffeine (limit to 200mg/day)
- Alcohol completely

"""
        if profile.pregnancy_trimester == 1:
            nutrition_advice += "\n**First Trimester Tip:** If you have morning sickness, try eating small, frequent meals and avoid spicy/greasy foods. Ginger tea can help!"
        
        return nutrition_advice + "\n\nConsult your doctor or nutritionist for a personalized meal plan based on your specific needs. 👩‍⚕️"
    
    # Exercise questions  
    if any(phrase in question_lower for phrase in ['exercise', 'workout', 'yoga', 'walking', 'physical activity']):
        return f"""Safe exercises during pregnancy:

✅ **Recommended:**
- Walking (30 minutes daily)
- Prenatal yoga
- Swimming/water aerobics
- Stationary cycling
- Light strength training

🚫 **Avoid:**
- Contact sports
- Activities with fall risk
- Hot yoga/Bikram
- Heavy weightlifting
- Exercises lying flat on back (after 1st trimester)

{context_prefix}listen to your body and stay hydrated. Stop if you feel dizzy, short of breath, or experience pain. Always consult your doctor before starting any new exercise routine! 💪"""
    
    # Morning sickness
    if any(phrase in question_lower for phrase in ['morning sickness', 'nausea', 'vomiting', 'throwing up', 'sick']):
        return """Morning sickness tips:

🍋 **Relief strategies:**
- Eat small, frequent meals (every 2-3 hours)
- Keep crackers by your bedside, eat before getting up
- Avoid spicy, greasy, or strong-smelling foods
- Try ginger tea or ginger candies
- Stay hydrated with small sips
- Get plenty of rest
- Vitamin B6 supplements (ask your doctor)
- Eat cold foods (they have less odor)

⚠️ **When to call doctor:**
- Can't keep any food or water down for 24 hours
- Losing weight
- Dark urine or decreased urination
- Dizziness or fainting

Morning sickness usually improves after the first trimester. Hang in there! 💚"""
    
    # Baby movement/kicks
    if any(phrase in question_lower for phrase in ['baby kick', 'baby move', 'movement', 'kicks', 'feel baby']):
        if profile.pregnancy_weeks:
            if profile.pregnancy_weeks < 18:
                return "You typically start feeling baby movements (called 'quickening') between weeks 18-25, often around week 20 for first-time moms. Second-time moms might feel it earlier around week 16. Be patient, your little one will start making their presence known soon! 👶"
            elif profile.pregnancy_weeks >= 18 and profile.pregnancy_weeks < 28:
                return f"""At week {profile.pregnancy_weeks}, you should start feeling baby movements if you haven't already!

**What to expect:**
- Early movements feel like flutters or butterflies
- Gradually become stronger, more distinct kicks
- More noticeable when you're sitting or lying down
- May increase after meals or sweet drinks

**Track movements:** In your third trimester, do daily kick counts. You should feel at least 10 movements in 2 hours.

If you haven't felt movements yet or notice a decrease, contact your doctor. 📞"""
            else:
                return f"""At week {profile.pregnancy_weeks}, you should be feeling regular baby movements!

**Kick counting:**
- Do this daily at the same time
- You should feel at least 10 movements within 2 hours
- Movements include kicks, rolls, and flutters

**When to call doctor IMMEDIATELY:**
- Sudden decrease in movements
- No movements for several hours
- Pattern change that concerns you

Your baby's movements are a sign of well-being. Trust your instincts - if something feels off, call your doctor right away! ⚠️"""
        return "Update your pregnancy week in your profile to get personalized information about baby movements!"
    
    # Ultrasound questions
    if any(phrase in question_lower for phrase in ['ultrasound', 'sonography', 'scan', 'imaging']):
        return """Pregnancy ultrasounds:

📅 **Typical schedule:**
- **6-9 weeks:** Dating scan (confirm pregnancy, due date)
- **11-14 weeks:** NT scan (Down syndrome screening)
- **18-22 weeks:** Anatomy scan (detailed baby examination)
- **28-32 weeks:** Growth scan (if needed)
- **36+ weeks:** Position check (if needed)

**What they check:**
- Baby's growth and development
- Heart rate
- Position and movement
- Amniotic fluid levels
- Placenta position
- Multiple babies

💡 **Tip:** You can upload your ultrasound images to your Medical Records Vault in Swasthyam and add baby's measurements for tracking!

Your doctor will recommend ultrasounds based on your specific situation. 🩺"""
    
    # Weight gain questions
    if any(phrase in question_lower for phrase in ['weight', 'gain', 'heavy', 'pounds', 'kg']):
        bmi_advice = ""
        if profile.bmi:
            if profile.bmi < 18.5:
                recommended = "28-40 lbs (12.5-18 kg)"
            elif profile.bmi < 25:
                recommended = "25-35 lbs (11.5-16 kg)"
            elif profile.bmi < 30:
                recommended = "15-25 lbs (7-11.5 kg)"
            else:
                recommended = "11-20 lbs (5-9 kg)"
            bmi_advice = f"\nBased on your pre-pregnancy BMI of {profile.bmi}, recommended total weight gain is: **{recommended}**"
        
        return f"""Pregnancy weight gain guidance:

**Healthy weight gain by trimester:**
- First trimester: 1-4 lbs total
- Second & third trimesters: About 1 lb per week

{bmi_advice}

**Where the weight goes:**
- Baby: 7-8 lbs
- Placenta: 1-2 lbs
- Amniotic fluid: 2 lbs
- Breast tissue: 1-2 lbs
- Blood & fluids: 6-8 lbs
- Fat stores: 6-8 lbs

Remember, every pregnancy is different. Focus on eating nutritious foods and staying active rather than the scale number. Discuss your specific situation with your doctor! 💪"""
    
    # Sleep questions
    if any(phrase in question_lower for phrase in ['sleep', 'insomnia', 'tired', 'exhausted', 'rest']):
        return """Sleep tips for pregnancy:

😴 **Better sleep strategies:**
- Sleep on your left side (improves blood flow)
- Use pregnancy pillow for support
- Elevate head if you have heartburn
- Empty bladder before bed
- Avoid caffeine after noon
- Light snack before bed (prevents hunger)
- Cool, dark room
- Establish bedtime routine

**Common issues:**
- Frequent urination (normal, unavoidable)
- Leg cramps (stretch, stay hydrated)
- Heartburn (elevate head, small meals)
- Anxiety (relaxation techniques, meditation)

It's normal to feel more tired, especially in first and third trimesters. Nap when possible and rest when needed. Your body is working hard growing a human! 🌙"""
    
    # ============================================================================
    # POSTPARTUM QUERIES
    # ============================================================================
    
    if profile.pregnancy_status == 'postpartum':
        if any(phrase in question_lower for phrase in ['postpartum', 'after birth', 'recovery', 'healing']):
            return """Postpartum recovery guidance:

🌸 **First 6 weeks:**
- Rest as much as possible
- Accept help from family/friends
- Gentle walking only (no intense exercise)
- Pelvic floor exercises (Kegels)
- Healthy nutrition for healing
- Stay hydrated (especially if breastfeeding)

**Physical recovery:**
- Vaginal delivery: 6-8 weeks
- C-section: 8-12 weeks
- Bleeding (lochia) for 4-6 weeks is normal

⚠️ **Call doctor if:**
- Heavy bleeding (soaking pad in 1 hour)
- Fever over 100.4°F
- Severe abdominal pain
- Foul-smelling discharge
- Redness/warmth at C-section incision

**Mental health:**
Baby blues are common (50-80% of moms). If sadness lasts >2 weeks or you have thoughts of harming yourself/baby, call your doctor immediately.

Take care of yourself so you can care for your baby! 💕"""
        
        if any(phrase in question_lower for phrase in ['breastfeed', 'nursing', 'milk', 'feeding']):
            return """Breastfeeding guidance:

🤱 **Getting started:**
- Start within first hour after birth
- Nurse on demand (8-12 times per day)
- Look for hunger cues (don't wait for crying)
- Ensure proper latch
- Both breasts each feeding
- Stay hydrated and well-nourished

**Common challenges:**
- Sore nipples: Check latch, use lanolin cream
- Engorgement: Nurse frequently, warm compress
- Low supply: Nurse more often, stay hydrated
- Clogged duct: Massage, warm compress, nurse

**When to call lactation consultant:**
- Baby isn't gaining weight
- Severe pain while nursing
- Concerns about milk supply
- Any breastfeeding difficulties

Don't hesitate to seek help - breastfeeding has a learning curve for both you and baby! 👶"""
    
    # ============================================================================
    # GENERAL HEALTH QUERIES
    # ============================================================================
    
    # Doctor appointment questions
    if any(phrase in question_lower for phrase in ['doctor', 'appointment', 'checkup', 'visit']):
        return """Prenatal appointment schedule:

📅 **Typical visit frequency:**
- Weeks 4-28: Every 4 weeks
- Weeks 28-36: Every 2 weeks
- Weeks 36-40: Every week
- Overdue: More frequent monitoring

**What happens at visits:**
- Weight and blood pressure check
- Urine test
- Fetal heartbeat check
- Measuring belly (fundal height)
- Discussion of symptoms/concerns
- Ultrasounds at specific weeks
- Blood tests as needed

**Questions to ask:**
- Write them down before visit
- Bring your partner if helpful
- Don't hesitate to ask anything!

💡 **Swasthyam tip:** Use our Appointment Scheduler to track upcoming visits and upload test results to your Medical Vault!

Always call your doctor between visits if you have concerns! 📞"""
    
    # Symptoms/discomfort
    if any(phrase in question_lower for phrase in ['pain', 'symptom', 'uncomfortable', 'ache', 'hurt']):
        return """Common pregnancy discomforts:

**Round ligament pain:**
- Sharp pains in lower belly/groin
- Relief: Change positions slowly, warm compress

**Back pain:**
- Relief: Good posture, prenatal massage, support belt

**Swelling (edema):**
- Normal in feet/ankles
- Relief: Elevate feet, reduce salt, stay hydrated

**Heartburn:**
- Relief: Small frequent meals, avoid triggers, elevate head

**Constipation:**
- Relief: Fiber, water, prunes, gentle exercise

⚠️ **Call doctor immediately for:**
- Severe abdominal pain
- Vaginal bleeding
- Severe headache
- Vision changes
- Severe swelling (face/hands)
- Decreased baby movement
- Fever >100.4°F
- Painful urination

Trust your instincts - if something doesn't feel right, call your healthcare provider! 🏥"""
    
    # ============================================================================
    # APP FEATURES & HELP
    # ============================================================================
    
    if any(phrase in question_lower for phrase in ['what can you do', 'help', 'how to use', 'features']):
        return """I'm your maternal health assistant! Here's how I can help:

💬 **Health Guidance:**
- Pregnancy symptoms and care
- Nutrition and exercise advice
- Postpartum recovery
- Baby care basics
- Warning signs to watch for

📁 **Medical Records Vault:**
- Upload ultrasounds, test results
- Organize by trimester
- Track baby's growth measurements
- Keep all health documents in one place

📅 **Appointment Tracking:**
- Schedule doctor visits
- Set reminders
- Link records to appointments

🤰 **Personalized Advice:**
- Based on your pregnancy week
- Considering your health profile
- Trimester-specific guidance

Ask me anything about pregnancy, health, or how to use Swasthyam features! I'm here to support your maternal health journey. 💚

**Remember:** I provide general guidance. Always consult your doctor for medical advice specific to your situation."""
    
    # Upload/vault questions
    if any(phrase in question_lower for phrase in ['upload', 'vault', 'ultrasound', 'record', 'document']):
        return """Using the Medical Records Vault:

📤 **To upload documents:**
1. Go to Medical Records Vault
2. Click "Upload Record"
3. Choose document type (Ultrasound, Blood Test, etc.)
4. Select your file (PDF, image, Word doc)
5. Enter trimester or pregnancy week
6. Add doctor name, hospital, key findings
7. Upload!

**For ultrasounds:**
- After uploading, you can add baby's measurements
- Track weight, length, heart rate
- Record gender reveal
- Store in timeline by trimester

**Benefits:**
- All records in one secure place
- Organized by trimester
- Easy to share with doctors
- Track baby's growth over time

Click on "Medical Records Vault" in the menu to get started! 📁"""
    
    # ============================================================================
    # DEFAULT RESPONSE
    # ============================================================================
    
    # If no pattern matched, provide helpful default
    return f"""I'm here to help with your maternal health questions! {context_prefix}

I can provide guidance on:
- Pregnancy symptoms and care
- Nutrition and exercise
- Baby development
- Postpartum recovery
- Warning signs
- Using Swasthyam features

Please feel free to ask specific questions about:
- Symptoms you're experiencing
- What to eat/avoid
- Exercise and activities
- Doctor appointments
- Baby movements
- Ultrasounds and tests

Or type "help" to see everything I can assist with!

**Important:** For specific medical concerns, please consult your healthcare provider. I provide general guidance to supplement professional medical care. 👩‍⚕️"""


def get_trimester_info(trimester):
    """Get trimester-specific information."""
    
    info = {
        1: """
**First Trimester (Weeks 1-13):**
- Baby's major organs developing
- Morning sickness common
- Extreme fatigue normal
- Frequent urination
- Food aversions/cravings
- Take prenatal vitamins daily
- Avoid alcohol, smoking, certain medications
""",
        2: """
**Second Trimester (Weeks 14-26):**
- "Honeymoon period" - more energy
- Baby bump showing
- Feel baby movements (weeks 18-25)
- Less nausea
- Glowing skin
- Anatomy scan around week 20
- May learn baby's gender
""",
        3: """
**Third Trimester (Weeks 27-40):**
- Baby gaining weight rapidly
- Increased discomfort (back pain, swelling)
- Braxton Hicks contractions
- Shortness of breath
- Frequent urination returns
- Nesting instinct
- Preparing for labor
- Weekly checkups from week 36
"""
    }
    
    return info.get(trimester, "")