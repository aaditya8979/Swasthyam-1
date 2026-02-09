"""
Main app views - Landing page, Dashboard, Error handlers.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

def landing_view(request):
    """
    Landing page - First entry point for users.
    """
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    context = {
        'show_navbar': False,  # Landing has its own hero section
    }
    return render(request, 'index.html', context)


@login_required
def dashboard_view(request):
    """
    Main dashboard after login.
    Shows personalized health summary and quick actions.
    """
    # Safety: Ensure profile exists (Superusers might miss this)
    if not hasattr(request.user, 'profile'):
        from users.models import UserProfile
        UserProfile.objects.create(user=request.user)

    profile = request.user.profile
    
    # --- FIX: Logic to handle Chat History safely ---
    # 1. Get the FULL QuerySet first (do not slice yet)
    all_chats = getattr(request.user, 'chat_history', None)
    
    # 2. Calculate stats on the full dataset
    total_chats = 0
    helpful_chats = 0
    recent_chats = []

    if all_chats:
        total_chats = all_chats.count()
        # Filter is allowed here because all_chats is not sliced
        helpful_chats = all_chats.filter(helpful=True).count()
        # 3. NOW slice the list for the dashboard display
        recent_chats = all_chats.order_by('-created_at')[:5]

    # --- End Fix ---

    recent_posts = getattr(request.user, 'posts', None)
    if recent_posts:
        recent_posts = recent_posts.order_by('-created_at')[:5]
    
    # Get upcoming milestones for pregnant users
    milestones = []
    if profile.pregnancy_status == 'pregnant' and profile.pregnancy_weeks:
        current_week = profile.pregnancy_weeks
        
        milestone_weeks = {
            12: _("End of First Trimester"),
            20: _("Anatomy Scan"),
            28: _("Start of Third Trimester"),
            36: _("Weekly Checkups Begin"),
            40: _("Due Date")
        }
        
        for week, description in milestone_weeks.items():
            if week > current_week:
                weeks_until = week - current_week
                milestones.append({
                    'week': week,
                    'description': description,
                    'weeks_until': weeks_until
                })
                if len(milestones) >= 3:
                    break
    
    context = {
        'profile': profile,
        'recent_chats': recent_chats,
        'recent_posts': recent_posts,
        'total_chats': total_chats,
        'helpful_chats': helpful_chats,
        'milestones': milestones,
        'show_setup_prompt': not profile.profile_completed,
    }
    return render(request, 'dashboard.html', context)


def about_view(request):
    """About Swasthyam page"""
    context = {
        'team': [
            {
                'name': 'Swasthyam Team',
                'role': 'Developers',
                'bio': _('Passionate about healthcare accessibility'),
            }
        ]
    }
    return render(request, 'about.html', context)


def privacy_view(request):
    return render(request, 'privacy.html')


def terms_view(request):
    return render(request, 'terms.html')


# Custom Error Handlers
def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)