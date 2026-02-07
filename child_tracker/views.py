from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Child, VaccineSchedule, VaccinationRecord, GrowthRecord, Medication, Milestone, MilestoneRecord, EmergencyContact
from .forms import ChildForm, GrowthRecordForm, MedicationForm, EmergencyContactForm
from datetime import date

@login_required
def tracker_home(request):
    """List all children or redirect to add child if none exist."""
    children = request.user.children.all()
    if not children.exists():
        return redirect('child_tracker:add_child')
    return render(request, 'child/home.html', {'children': children})

@login_required
def add_child(request):
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            
            # AUTO-POPULATE LOGIC
            # 1. Create Vaccination Records from Schedule
            vaccines = VaccineSchedule.objects.all()
            vaccine_records = [
                VaccinationRecord(child=child, vaccine=v) for v in vaccines
            ]
            VaccinationRecord.objects.bulk_create(vaccine_records)
            
            # 2. Create Milestone Records
            milestones = Milestone.objects.all()
            milestone_records = [
                MilestoneRecord(child=child, milestone=m) for m in milestones
            ]
            MilestoneRecord.objects.bulk_create(milestone_records)
            
            messages.success(request, f'{child.name} added successfully!')
            return redirect('child_tracker:child_detail', child_id=child.id)
    else:
        form = ChildForm()
    return render(request, 'child/child_form.html', {'form': form, 'title': 'Add Child'})

@login_required
def child_detail(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    # Get summary data
    next_vaccine = child.vaccinations.filter(is_completed=False).order_by('vaccine__age_in_months').first()
    latest_growth = child.growth_records.first()
    active_meds = child.medications.filter(is_active=True)
    
    context = {
        'child': child,
        'next_vaccine': next_vaccine,
        'latest_growth': latest_growth,
        'active_meds': active_meds
    }
    return render(request, 'child/child_detail.html', context)

@login_required
def vaccine_tracker(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    records = child.vaccinations.select_related('vaccine').order_by('vaccine__age_in_months')
    return render(request, 'child/vaccine_tracker.html', {'child': child, 'records': records})

@login_required
def mark_vaccine_complete(request, child_id, record_id):
    """AJAX endpoint to toggle vaccine status"""
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    record = get_object_or_404(VaccinationRecord, id=record_id, child=child)
    
    if request.method == 'POST':
        record.is_completed = not record.is_completed
        if record.is_completed:
            record.administered_date = date.today()
        else:
            record.administered_date = None
        record.save()
        return JsonResponse({'success': True, 'is_completed': record.is_completed})
    return JsonResponse({'success': False}, status=400)

@login_required
def growth_tracker(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    records = child.growth_records.all()
    return render(request, 'child/growth_tracker.html', {'child': child, 'records': records})

@login_required
def add_growth_record(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    if request.method == 'POST':
        form = GrowthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.child = child
            record.save()
            messages.success(request, 'Growth record added.')
            return redirect('child_tracker:growth_tracker', child_id=child.id)
    else:
        form = GrowthRecordForm()
    return render(request, 'child/generic_form.html', {'form': form, 'title': 'Add Growth Record'})

# --- Placeholders for other views to prevent crashes ---
@login_required
def edit_child(request, child_id): pass 
@login_required
def delete_child(request, child_id): pass
@login_required
def medication_list(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    return render(request, 'child/medication_list.html', {'child': child})
@login_required
def add_medication(request, child_id): pass
@login_required
def milestone_tracker(request, child_id): 
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    records = child.milestone_records.select_related('milestone').all()
    return render(request, 'child/milestone_tracker.html', {'child': child, 'records': records})
@login_required
def mark_milestone(request, child_id, record_id): pass
@login_required
def emergency_info(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    contacts = child.emergency_contacts.all()
    return render(request, 'child/emergency_info.html', {'child': child, 'contacts': contacts})