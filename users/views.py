"""
Views for user authentication and profile management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .forms import UserRegisterForm, UserLoginForm, ProfileSetupForm, ProfileUpdateForm
from .models import UserProfile, MedicalDisclaimer
import json


def auth_view(request):
    """
    Combined login/signup view with toggle functionality.
    Returns a split-card design.
    """
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    login_form = UserLoginForm()
    register_form = UserRegisterForm()
    
    if request.method == 'POST':
        # Determine which form was submitted
        if 'login_submit' in request.POST:
            login_form = UserLoginForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, _('Welcome back, %(username)s!') % {'username': user.username})
                    
                    # Redirect to profile setup if profile is incomplete
                    if not user.profile.profile_completed:
                        return redirect('users:profile_setup')
                    
                    return redirect('main:dashboard')
            else:
                messages.error(request, _('Invalid username or password.'))
        
        elif 'register_submit' in request.POST:
            register_form = UserRegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                username = register_form.cleaned_data.get('username')
                messages.success(request, _('Account created successfully! Please complete your profile.'))
                login(request, user)
                return redirect('users:profile_setup')
            else:
                messages.error(request, _('Please correct the errors below.'))
    
    context = {
        'login_form': login_form,
        'register_form': register_form,
    }
    return render(request, 'auth.html', context)


@login_required
def profile_setup_view(request):
    """
    Post-registration profile setup.
    Captures critical health data for RAG context.
    """
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=profile)
        
        # Check medical disclaimer acceptance
        if 'accept_disclaimer' not in request.POST:
            messages.error(request, _('You must accept the medical disclaimer to continue.'))
        elif form.is_valid():
            profile = form.save(commit=False)
            profile.profile_completed = True
            profile.medical_disclaimer_accepted = True
            profile.save()
            
            # Record disclaimer acceptance
            disclaimer_text = "I understand that Swasthyam provides health information and is not a substitute for professional medical advice. I will consult healthcare professionals for medical decisions."
            MedicalDisclaimer.objects.create(
                user=request.user,
                disclaimer_text=disclaimer_text,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, _('Profile completed! Welcome to Swasthyam.'))
            return redirect('main:dashboard')
    else:
        form = ProfileSetupForm(instance=profile)
    
    context = {
        'form': form,
        'is_setup': True,
    }
    return render(request, 'users/profile_setup.html', context)


@login_required
def profile_view(request):
    """Display user profile with health stats"""
    profile = request.user.profile
    
    # Calculate some stats
    chat_count = request.user.chat_history.count()
    forum_posts = request.user.posts.count() if hasattr(request.user, 'posts') else 0
    
    context = {
        'profile': profile,
        'chat_count': chat_count,
        'forum_posts': forum_posts,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Update User model fields
            user = request.user
            user.email = form.cleaned_data.get('email', user.email)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.save()
            
            profile.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    context = {
        'form': form,
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def delete_account_view(request):
    """Allow users to delete their account (GDPR compliance)"""
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            # Log the user out and delete
            logout(request)
            user.delete()
            messages.success(request, _('Your account has been deleted. We\'re sorry to see you go.'))
            return redirect('main:landing')
        else:
            messages.error(request, _('Incorrect password. Account not deleted.'))
    
    return render(request, 'users/delete_account.html')


def logout_view(request):
    """Log the user out"""
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('main:landing')


@login_required
@require_http_methods(["POST"])
def toggle_dark_mode(request):
    """AJAX endpoint to toggle dark mode preference"""
    try:
        profile = request.user.profile
        profile.dark_mode_enabled = not profile.dark_mode_enabled
        profile.save()
        
        return JsonResponse({
            'success': True,
            'dark_mode_enabled': profile.dark_mode_enabled
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_language_preference(request):
    """AJAX endpoint to update language preference"""
    try:
        data = json.loads(request.body)
        language = data.get('language')
        
        if language in ['en', 'hi']:
            profile = request.user.profile
            profile.preferred_language = language
            profile.save()
            
            return JsonResponse({
                'success': True,
                'language': language
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid language'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# Helper function
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip