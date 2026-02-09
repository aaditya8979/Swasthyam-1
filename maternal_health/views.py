"""
Maternal Health RAG Chatbot - Context-Aware AI Assistant.
Updated for OpenAI v1.0+ with Predefined Polite Responses.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.translation import gettext as _
from users.models import ChatHistory
from openai import OpenAI
import json
from datetime import datetime

# Initialize Modern OpenAI Client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def maternal_home_view(request):
    """Maternal health landing page with chat/forum split."""
    profile = request.user.profile
    
    # Safety check if chat_history relation doesn't exist yet
    recent_chats = getattr(request.user, 'chat_history', None)
    if recent_chats:
        recent_chats = recent_chats.order_by('-created_at')[:10]
    
    context = {
        'profile': profile,
        'recent_chats': recent_chats,
        'resources': get_maternal_resources(), # Added resources to context
    }
    return render(request, 'maternal/home.html', context)

@login_required
def chat_view(request):
    """Main RAG chatbot interface."""
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
    Checks predefined answers first to save API costs.
    """
    try:
        data = json.loads(request.body)
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return JsonResponse({'success': False, 'error': _('Please enter a question.')}, status=400)
        
        profile = request.user.profile
        
        # --- 1. CHECK PREDEFINED ANSWERS (Save API Cost) ---
        ai_answer = get_predefined_answer(user_question, profile)
        
        # --- 2. IF NO PREDEFINED ANSWER, CALL OPENAI ---
        if not ai_answer:
            try:
                system_prompt = build_system_prompt(profile)
                
                # NEW v1.0 SYNTAX
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_question}
                    ],
                    temperature=0.7,
                    max_tokens=400,
                )
                ai_answer = response.choices[0].message.content.strip()
                
            except Exception as e:
                # Log the specific error for debugging
                print(f"OpenAI API Error: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('AI service is temporarily unavailable. Please try again.')
                }, status=503)

        # --- 3. SAVE CONVERSATION ---
        chat_record = ChatHistory.objects.create(
            user=request.user,
            question=user_question,
            answer=ai_answer,
            user_age_at_time=profile.age,
            pregnancy_weeks_at_time=profile.pregnancy_weeks,
        )
        
        return JsonResponse({
            'success': True,
            'answer': ai_answer,
            'chat_id': chat_record.id,
            'timestamp': chat_record.created_at.strftime("%I:%M %p")
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def rate_chat(request):
    """Allow users to rate chatbot responses."""
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        helpful = data.get('helpful')
        
        chat = ChatHistory.objects.get(id=chat_id, user=request.user)
        chat.helpful = helpful
        chat.save()
        return JsonResponse({'success': True})
    except Exception:
        return JsonResponse({'success': False}, status=400)

@login_required
def chat_history_view(request):
    """View all past chat conversations."""
    chats = request.user.chat_history.order_by('-created_at')
    from itertools import groupby
    
    grouped_chats = {}
    for key, group in groupby(chats, lambda x: x.created_at.date()):
        grouped_chats[key] = list(group)
    
    return render(request, 'maternal/chat_history.html', {'grouped_chats': grouped_chats})

# --- Helper Functions ---

def get_predefined_answer(question, profile):
    """
    Returns a static polite response for common greetings/questions.
    Returns None if the question requires AI processing.
    """
    q = question.lower().strip().rstrip('?!.')
    
    # Greetings
    if q in ['hi', 'hello', 'hey', 'namaste', 'greetings']:
        return _(f"Namaste, {profile.user.first_name or 'Friend'}! I am here to support your health journey. How are you feeling today?")
        
    # Identity
    if q in ['who are you', 'what are you', 'what is this']:
        return _("I am Swasthyam's AI Health Assistant. I am here to provide guidance on maternal and child health based on your profile.")
        
    # Gratitude
    if q in ['thank you', 'thanks', 'thx', 'thanks a lot']:
        return _("You are very welcome! Take care of yourself. Is there anything else you need?")
        
    # Well-being
    if q in ['how are you', 'how are you doing']:
        return _("I am just a computer program, but I am functioning perfectly and ready to help you! How are you?")
    
    # Default Help
    if q in ['help', 'help me', 'support']:
        return _("I can help you with pregnancy tips, nutrition advice, tracking your child's growth, or answering general health questions. What's on your mind?")

    # Emergency keywords (Safety First)
    if any(word in q for word in ['bleeding', 'severe pain', 'faint', 'emergency', 'suicide']):
        return _("⚠️ **IMPORTANT:** If you are experiencing a medical emergency, severe pain, or bleeding, please stop using this chat and visit the nearest hospital immediately or call an ambulance (102/108).")

    return None

def build_system_prompt(profile):
    """Construct context-aware system prompt."""
    prompt = """You are a compassionate, medical-aware AI assistant for Swasthyam. 
    Your goal is to provide supportive, accurate, and brief health information.
    ALWAYS include a disclaimer to consult a doctor for medical decisions.
    """
    
    # Personalization
    if profile.pregnancy_status == 'pregnant':
        prompt += f"\nThe user is currently {profile.pregnancy_weeks} weeks pregnant."
    elif profile.pregnancy_status == 'postpartum':
        prompt += "\nThe user recently gave birth."
        
    if profile.age:
        prompt += f"\nUser age: {profile.age}."
        
    return prompt

def get_maternal_resources():
    """Static resources for the sidebar."""
    return {
        'emergency': {
            'title': _('Emergency'),
            'content': [_('Ambulance: 102'), _('Women Helpline: 181')]
        },
        'nutrition': {
            'title': _('Nutrition'),
            'content': [_('Iron-rich foods'), _('Stay Hydrated')]
        }
    }