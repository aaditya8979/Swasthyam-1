"""
URL patterns for the child tracker app.
"""

from django.urls import path
from . import views

app_name = 'child_tracker'

urlpatterns = [
    path('', views.tracker_home, name='home'),
    path('child/add/', views.add_child, name='add_child'),
    path('child/<int:child_id>/', views.child_detail, name='child_detail'),
    path('child/<int:child_id>/edit/', views.edit_child, name='edit_child'),
    path('child/<int:child_id>/delete/', views.delete_child, name='delete_child'),
    
    # Vaccinations
    path('child/<int:child_id>/vaccines/', views.vaccine_tracker, name='vaccine_tracker'),
    path('child/<int:child_id>/vaccine/<int:record_id>/complete/', views.mark_vaccine_complete, name='mark_vaccine_complete'),
    
    # Growth
    path('child/<int:child_id>/growth/', views.growth_tracker, name='growth_tracker'),
    path('child/<int:child_id>/growth/add/', views.add_growth_record, name='add_growth_record'),
    
    # Medications
    path('child/<int:child_id>/medications/', views.medication_list, name='medication_list'),
    path('child/<int:child_id>/medication/add/', views.add_medication, name='add_medication'),
    
    # Milestones - Enhanced Interactive Tracker
    path('child/<int:child_id>/milestones/', views.milestone_tracker, name='milestone_tracker'),
    path('child/<int:child_id>/milestone/<int:record_id>/achieve/', views.mark_milestone, name='mark_milestone'),
    
    # Our Memories - Photo & Video Gallery
    path('child/<int:child_id>/memories/', views.memories_gallery, name='memories_gallery'),
    path('child/<int:child_id>/memories/add/', views.add_memory, name='add_memory'),
    path('child/<int:child_id>/memory/<int:memory_id>/favorite/', views.toggle_favorite_memory, name='toggle_favorite_memory'),
    path('child/<int:child_id>/memory/<int:memory_id>/delete/', views.delete_memory, name='delete_memory'),
]