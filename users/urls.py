
"""
URL patterns for the users app.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile Management
    path('profile/setup/', views.profile_setup_view, name='profile_setup'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/delete/', views.delete_account_view, name='delete_account'),
    
    # AJAX Endpoints
    path('api/toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path('api/update-language/', views.update_language_preference, name='update_language'),
]