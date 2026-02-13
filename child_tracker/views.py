"""
Child Tracker Views - Enhanced with Interactive Milestones & Memories Gallery
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from django.db.models import Count, Q
from .models import (
    Child, VaccineSchedule, VaccinationRecord, 
    GrowthRecord, Medication, Milestone, MilestoneRecord, Memory
)
from .forms import (
    ChildForm, GrowthRecordForm, MedicationForm, 
    MemoryForm, MilestoneAchievementForm
)
from datetime import date, timedelta
import json


@login_required
def tracker_home(request):
    """
    List all children or redirect to add child if none exist.
    """
    children = request.user.children.all()
    
    if not children.exists():
        messages.info(request, _('Add your first child to start tracking their health journey!'))
        return redirect('child_tracker:add_child')
    
    # Get summary statistics for each child
    children_data = []
    for child in children:
        children_data.append({
            'child': child,
            'pending_vaccines': child.vaccinations.filter(is_completed=False, is_overdue=False).count(),
            'overdue_vaccines': child.vaccinations.filter(is_overdue=True).count(),
            'recent_milestones': child.milestone_records.filter(achieved=True).order_by('-achieved_date')[:3],
            'total_memories': child.memories.count(),
            'latest_memory': child.memories.first(),
        })
    
    context = {
        'children_data': children_data,
    }
    return render(request, 'child/home.html', context)


@login_required
def add_child(request):
    """
    Add a new child and auto-populate vaccination and milestone records.
    """
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            
            # AUTO-POPULATE LOGIC
            # 1. Create Vaccination Records from Schedule
            vaccines = VaccineSchedule.objects.all()
            if vaccines.exists():
                vaccine_records = [
                    VaccinationRecord(child=child, vaccine=v) for v in vaccines
                ]
                VaccinationRecord.objects.bulk_create(vaccine_records)
            
            # 2. Create Milestone Records
            milestones = Milestone.objects.all()
            if milestones.exists():
                milestone_records = [
                    MilestoneRecord(child=child, milestone=m) for m in milestones
                ]
                MilestoneRecord.objects.bulk_create(milestone_records)
            
            messages.success(request, _(f'{child.name} added successfully! Start tracking their journey.'))
            return redirect('child_tracker:child_detail', child_id=child.id)
    else:
        form = ChildForm()
    
    context = {
        'form': form,
        'title': _('Add Child'),
        'submit_text': _('Add Child'),
    }
    return render(request, 'child/child_form.html', context)


@login_required
def child_detail(request, child_id):
    """
    Child overview dashboard with key stats and recent activity.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    # Vaccination stats
    total_vaccines = child.vaccinations.count()
    completed_vaccines = child.vaccinations.filter(is_completed=True).count()
    next_vaccine = child.vaccinations.filter(
        is_completed=False
    ).order_by('vaccine__age_in_months').first()
    
    # Growth stats
    latest_growth = child.growth_records.first()
    growth_count = child.growth_records.count()
    
    # Milestone stats
    total_milestones = child.milestone_records.count()
    achieved_milestones = child.milestone_records.filter(achieved=True).count()
    recent_achievements = child.milestone_records.filter(
        achieved=True
    ).order_by('-achieved_date')[:5]
    
    # Medication
    active_meds = child.medications.filter(is_active=True)
    
    # Memories
    recent_memories = child.memories.all()[:6]
    total_memories = child.memories.count()
    
    context = {
        'child': child,
        'total_vaccines': total_vaccines,
        'completed_vaccines': completed_vaccines,
        'next_vaccine': next_vaccine,
        'latest_growth': latest_growth,
        'growth_count': growth_count,
        'total_milestones': total_milestones,
        'achieved_milestones': achieved_milestones,
        'recent_achievements': recent_achievements,
        'active_meds': active_meds,
        'recent_memories': recent_memories,
        'total_memories': total_memories,
    }
    return render(request, 'child/child_detail.html', context)


@login_required
def edit_child(request, child_id):
    """
    Edit child information.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, _(f'{child.name}\'s information updated successfully!'))
            return redirect('child_tracker:child_detail', child_id=child.id)
    else:
        form = ChildForm(instance=child)
    
    context = {
        'form': form,
        'title': _(f'Edit {child.name}'),
        'submit_text': _('Update'),
        'child': child,
    }
    return render(request, 'child/child_form.html', context)


@login_required
def delete_child(request, child_id):
    """
    Delete child profile (with confirmation).
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    if request.method == 'POST':
        child_name = child.name
        child.delete()
        messages.success(request, _(f'{child_name}\'s profile has been deleted.'))
        return redirect('child_tracker:home')
    
    context = {
        'child': child,
    }
    return render(request, 'child/child_confirm_delete.html', context)


# ============================================================================
# VACCINATION TRACKER
# ============================================================================

@login_required
def vaccine_tracker(request, child_id):
    """
    View all vaccination records with status tracking.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    records = child.vaccinations.select_related('vaccine').order_by('vaccine__age_in_months')
    
    # Categorize vaccines
    completed = records.filter(is_completed=True)
    upcoming = records.filter(is_completed=False, is_overdue=False)
    overdue = records.filter(is_overdue=True)
    
    context = {
        'child': child,
        'records': records,
        'completed': completed,
        'upcoming': upcoming,
        'overdue': overdue,
    }
    return render(request, 'child/vaccine_tracker.html', context)


@login_required
@require_http_methods(["POST"])
def mark_vaccine_complete(request, child_id, record_id):
    """
    AJAX endpoint to toggle vaccine completion status.
    """
    try:
        child = get_object_or_404(Child, id=child_id, parent=request.user)
        record = get_object_or_404(VaccinationRecord, id=record_id, child=child)
        
        # Toggle completion
        record.is_completed = not record.is_completed
        
        if record.is_completed:
            record.administered_date = date.today()
            message = _(f'{record.vaccine.vaccine_name} marked as completed!')
        else:
            record.administered_date = None
            message = _(f'{record.vaccine.vaccine_name} marked as pending.')
        
        record.save()
        
        return JsonResponse({
            'success': True,
            'is_completed': record.is_completed,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ============================================================================
# GROWTH TRACKER
# ============================================================================

@login_required
def growth_tracker(request, child_id):
    """
    View growth records and charts.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    records = child.growth_records.all()
    
    # Prepare data for charts
    chart_data = {
        'dates': [r.date.strftime('%Y-%m-%d') for r in reversed(records)],
        'weights': [float(r.weight) for r in reversed(records)],
        'heights': [float(r.height) for r in reversed(records)],
    }
    
    context = {
        'child': child,
        'records': records,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'child/growth_tracker.html', context)


@login_required
def add_growth_record(request, child_id):
    """
    Add a new growth measurement.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    if request.method == 'POST':
        form = GrowthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.child = child
            record.save()
            messages.success(request, _('Growth record added successfully!'))
            return redirect('child_tracker:growth_tracker', child_id=child.id)
    else:
        form = GrowthRecordForm()
    
    context = {
        'form': form,
        'title': _(f'Add Growth Record for {child.name}'),
        'child': child,
    }
    return render(request, 'child/generic_form.html', context)


# ============================================================================
# MEDICATION TRACKER
# ============================================================================

@login_required
def medication_list(request, child_id):
    """
    View all medications (active and past).
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    active_meds = child.medications.filter(is_active=True)
    past_meds = child.medications.filter(is_active=False)
    
    context = {
        'child': child,
        'active_meds': active_meds,
        'past_meds': past_meds,
    }
    return render(request, 'child/medication_list.html', context)


@login_required
def add_medication(request, child_id):
    """
    Add a new medication record.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.child = child
            medication.save()
            messages.success(request, _('Medication added successfully!'))
            return redirect('child_tracker:medication_list', child_id=child.id)
    else:
        form = MedicationForm()
    
    context = {
        'form': form,
        'title': _(f'Add Medication for {child.name}'),
        'child': child,
    }
    return render(request, 'child/generic_form.html', context)


# ============================================================================
# MILESTONE TRACKER - ENHANCED INTERACTIVE VERSION
# ============================================================================

@login_required
# ... (Keep existing imports)

@login_required
def milestone_tracker(request, child_id):
    """
    Interactive milestone tracker.
    AUTO-FIX: Creates missing records on page load.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    # --- AUTO-POPULATE MISSING RECORDS ---
    # This ensures the page is never blank
    all_milestones = Milestone.objects.all()
    existing_records = child.milestone_records.values_list('milestone_id', flat=True)
    
    missing_records = [
        MilestoneRecord(child=child, milestone=m) 
        for m in all_milestones 
        if m.id not in existing_records
    ]
    
    if missing_records:
        MilestoneRecord.objects.bulk_create(missing_records)
    # -------------------------------------

    # Get records with related milestone data
    records = child.milestone_records.select_related('milestone').all()
    
    # ... (Keep the rest of your filtering/progress logic here) ...
    
    # Example logic (restore your previous context dictionary):
    progress = {
        'motor': 0, 'social': 0, 'language': 0, 'cognitive': 0
    }
    
    context = {
        'child': child,
        'motor_milestones': records.filter(milestone__category='motor'),
        'social_milestones': records.filter(milestone__category='social'),
        'language_milestones': records.filter(milestone__category='language'),
        'cognitive_milestones': records.filter(milestone__category='cognitive'),
        'progress': progress, 
        'overall_progress': 0, 
    }
    return render(request, 'child/milestone_tracker.html', context)


@login_required
def vaccine_tracker(request, child_id):
    """
    View all vaccination records.
    AUTO-FIX: Creates missing records on page load.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    # --- AUTO-POPULATE MISSING VACCINES ---
    all_schedules = VaccineSchedule.objects.all()
    existing_vaccines = child.vaccinations.values_list('vaccine_id', flat=True)
    
    missing_vaccines = [
        VaccinationRecord(child=child, vaccine=v)
        for v in all_schedules
        if v.id not in existing_vaccines
    ]
    
    if missing_vaccines:
        VaccinationRecord.objects.bulk_create(missing_vaccines)
    # --------------------------------------

    records = child.vaccinations.select_related('vaccine').order_by('vaccine__age_in_months')
    
    context = {
        'child': child,
        'records': records,
        'completed': records.filter(is_completed=True),
        'upcoming': records.filter(is_completed=False),
    }
    return render(request, 'child/vaccine_tracker.html', context)

@login_required
@require_http_methods(["POST"])
def mark_milestone(request, child_id, record_id):
    """
    AJAX endpoint to mark milestone as achieved with optional notes.
    """
    try:
        child = get_object_or_404(Child, id=child_id, parent=request.user)
        record = get_object_or_404(MilestoneRecord, id=record_id, child=child)
        
        data = json.loads(request.body)
        achieved = data.get('achieved', True)
        notes = data.get('notes', '')
        
        record.achieved = achieved
        
        if achieved:
            record.achieved_date = date.today()
            record.notes = notes
            message = _(f'🎉 {record.milestone.title} achieved! Great progress!')
        else:
            record.achieved_date = None
            record.notes = ''
            message = _(f'{record.milestone.title} unmarked.')
        
        record.save()
        
        return JsonResponse({
            'success': True,
            'achieved': record.achieved,
            'achieved_date': record.achieved_date.strftime('%Y-%m-%d') if record.achieved_date else None,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ============================================================================
# OUR MEMORIES - PHOTO & VIDEO GALLERY
# ============================================================================

@login_required
def memories_gallery(request, child_id):
    """
    View all memories (photos and videos) in a beautiful gallery.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    # Filter options
    filter_type = request.GET.get('type', 'all')  # all, photo, video
    filter_favorite = request.GET.get('favorite', 'all')  # all, favorites
    
    memories = child.memories.all()
    
    if filter_type != 'all':
        memories = memories.filter(media_type=filter_type)
    
    if filter_favorite == 'favorites':
        memories = memories.filter(is_favorite=True)
    
    # Group by year and month for timeline view
    memories_by_period = {}
    for memory in memories:
        year_month = memory.memory_date.strftime('%Y-%m')
        if year_month not in memories_by_period:
            memories_by_period[year_month] = []
        memories_by_period[year_month].append(memory)
    
    # Statistics
    total_memories = child.memories.count()
    photo_count = child.memories.filter(media_type='photo').count()
    video_count = child.memories.filter(media_type='video').count()
    favorite_count = child.memories.filter(is_favorite=True).count()
    
    context = {
        'child': child,
        'memories': memories,
        'memories_by_period': memories_by_period,
        'total_memories': total_memories,
        'photo_count': photo_count,
        'video_count': video_count,
        'favorite_count': favorite_count,
        'filter_type': filter_type,
        'filter_favorite': filter_favorite,
    }
    return render(request, 'child/memories_gallery.html', context)


@login_required
def add_memory(request, child_id):
    """
    Upload a new photo or video memory.
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    if request.method == 'POST':
        form = MemoryForm(request.POST, request.FILES)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.child = child
            
            # Auto-detect media type from file extension
            if memory.file:
                file_ext = memory.file.name.lower().split('.')[-1]
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    memory.media_type = 'photo'
                elif file_ext in ['mp4', 'mov', 'avi', 'mkv']:
                    memory.media_type = 'video'
            
            memory.save()
            messages.success(request, _('Memory added successfully! 📸'))
            
            # Return JSON for AJAX upload
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'memory_id': memory.id,
                    'file_url': memory.file.url,
                    'title': memory.title,
                })
            
            return redirect('child_tracker:memories_gallery', child_id=child.id)
    else:
        form = MemoryForm()
    
    context = {
        'form': form,
        'title': _(f'Add Memory for {child.name}'),
        'child': child,
    }
    return render(request, 'child/add_memory.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_favorite_memory(request, child_id, memory_id):
    """
    AJAX endpoint to toggle memory favorite status.
    """
    try:
        child = get_object_or_404(Child, id=child_id, parent=request.user)
        memory = get_object_or_404(Memory, id=memory_id, child=child)
        
        memory.is_favorite = not memory.is_favorite
        memory.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': memory.is_favorite,
            'message': _('Added to favorites!') if memory.is_favorite else _('Removed from favorites.')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def delete_memory(request, child_id, memory_id):
    """
    Delete a memory (with confirmation).
    """
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    memory = get_object_or_404(Memory, id=memory_id, child=child)
    
    if request.method == 'POST':
        memory.delete()
        messages.success(request, _('Memory deleted.'))
        return redirect('child_tracker:memories_gallery', child_id=child.id)
    
    context = {
        'child': child,
        'memory': memory,
    }
    return render(request, 'child/memory_confirm_delete.html', context)