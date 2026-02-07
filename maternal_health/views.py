"""
Maternal Health RAG Chatbot - Context-Aware AI Assistant.
Uses OpenAI API with user profile data for personalized responses.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.translation import gettext as _
from users.models import ChatHistory
import openai
import json
from datetime import datetime

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY


@login_required
def maternal_home_view(request):
    """
    Maternal health landing page with chat/forum split.
    """
    profile = request.user.profile
    recent_chats = request.user.chat_history.order_by('-created_at')[:10]
    
    context = {
        'profile': profile,
        'recent_chats': recent_chats,
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
        
        # Build context-aware system prompt
        system_prompt = build_system_prompt(profile)
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper responses
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        ai_answer = response.choices[0].message['content'].strip()
        
        # Save to chat history
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
            'timestamp': chat_record.created_at.isoformat()
        })
        
    except openai.error.OpenAIError as e:
        return JsonResponse({
            'success': False,
            'error': _('AI service is currently unavailable. Please try again later.')
        }, status=503)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': _('An error occurred. Please try again.')
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
    from datetime import date
    
    grouped_chats = {}
    for key, group in groupby(chats, lambda x: x.created_at.date()):
        grouped_chats[key] = list(group)
    
    context = {
        'grouped_chats': grouped_chats,
    }
    return render(request, 'maternal/chat_history.html', context)


# Helper Functions

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