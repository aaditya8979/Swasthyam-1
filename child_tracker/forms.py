"""
Forms for Child Tracker app.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Child, GrowthRecord, Medication, Memory, MilestoneRecord


class ChildForm(forms.ModelForm):
    """Form for adding/editing child information."""
    
    class Meta:
        model = Child
        fields = [
            'name', 'gender', 'date_of_birth', 'birth_weight', 
            'birth_height', 'blood_group', 'allergies', 
            'medical_conditions', 'photo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Child\'s name')
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'type': 'date'
            }),
            'birth_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Weight in kg'),
                'step': '0.01'
            }),
            'birth_height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Height in cm'),
                'step': '0.01'
            }),
            'blood_group': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('e.g., O+, A-, AB+')
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('List any known allergies'),
                'rows': 3
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Any chronic conditions'),
                'rows': 3
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'accept': 'image/*'
            }),
        }


class GrowthRecordForm(forms.ModelForm):
    """Form for adding growth measurements."""
    
    class Meta:
        model = GrowthRecord
        fields = ['date', 'weight', 'height', 'head_circumference', 'notes', 'measured_by']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'type': 'date'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Weight in kg'),
                'step': '0.01'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Height in cm'),
                'step': '0.01'
            }),
            'head_circumference': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'rows': 3}),
            'measured_by': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
        }


class MedicationForm(forms.ModelForm):
    """Form for tracking medications."""
    
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'frequency', 'start_date', 'end_date',
                  'prescribed_for', 'prescribed_by', 'instructions', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'dosage': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'frequency': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'type': 'date'}),
            'prescribed_for': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'prescribed_by': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'instructions': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-green-600'}),
        }


class MemoryForm(forms.ModelForm):
    """Form for uploading photos and videos."""
    
    class Meta:
        model = Memory
        fields = ['file', 'title', 'description', 'memory_date', 'is_milestone', 'tags', 'is_favorite']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border',
                'accept': 'image/*,video/*',
                'id': 'memory-file-input'
            }),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'rows': 4}),
            'memory_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'type': 'date'}),
            'is_milestone': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-green-600'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border'}),
            'is_favorite': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-green-600'}),
        }


class MilestoneAchievementForm(forms.ModelForm):
    """Form for marking milestones."""
    
    class Meta:
        model = MilestoneRecord
        fields = ['achieved', 'achieved_date', 'notes']
        widgets = {
            'achieved': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-green-600'}),
            'achieved_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border', 'rows': 3}),
        }