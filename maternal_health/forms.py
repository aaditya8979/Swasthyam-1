"""
Forms for Maternal Health - Medical Records & Appointments.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import MedicalRecord, UltrasoundImage, AppointmentReminder


class MedicalRecordForm(forms.ModelForm):
    """
    Form for uploading medical records.
    """
    
    class Meta:
        model = MedicalRecord
        fields = [
            'record_type', 'title', 'description', 'document',
            'trimester', 'pregnancy_week', 'record_date',
            'doctor_name', 'hospital_name', 'key_findings',
            'tags', 'is_important'
        ]
        widgets = {
            'record_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('e.g., 20-Week Anatomy Scan, Blood Test Week 12')
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Any notes about this record'),
                'rows': 3
            }),
            'document': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'accept': 'image/*,.pdf,.doc,.docx',
                'id': 'document-upload'
            }),
            'trimester': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500'
            }),
            'pregnancy_week': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Week (0-42)'),
                'min': 0,
                'max': 42
            }),
            'record_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'type': 'date'
            }),
            'doctor_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Doctor name (optional)')
            }),
            'hospital_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Hospital/Clinic name (optional)')
            }),
            'key_findings': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Important results or findings (e.g., "Baby weight: 2.5kg, Everything normal")'),
                'rows': 3
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Tags: diabetes, blood pressure, etc.')
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-green-600 rounded focus:ring-green-500'
            }),
        }


class UltrasoundDetailsForm(forms.ModelForm):
    """
    Form for adding detailed ultrasound information.
    """
    
    class Meta:
        model = UltrasoundImage
        fields = [
            'baby_weight_grams', 'baby_length_cm', 'head_circumference_cm',
            'heart_rate_bpm', 'baby_position', 'gender_revealed', 'gender',
            'amniotic_fluid_level', 'placenta_position'
        ]
        widgets = {
            'baby_weight_grams': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Weight in grams')
            }),
            'baby_length_cm': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Length in cm'),
                'step': '0.01'
            }),
            'head_circumference_cm': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Head circumference in cm'),
                'step': '0.01'
            }),
            'heart_rate_bpm': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Heart rate (beats per minute)')
            }),
            'baby_position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('e.g., Head down, Breech')
            }),
            'gender_revealed': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-green-600'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500'
            }),
            'amniotic_fluid_level': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('e.g., Normal, Low, High')
            }),
            'placenta_position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('e.g., Anterior, Posterior')
            }),
        }


class AppointmentForm(forms.ModelForm):
    """
    Form for scheduling appointments.
    """
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'appointment_type', 'title', 'description',
            'appointment_date', 'appointment_time',
            'doctor_name', 'hospital_name', 'address'
        ]
        widgets = {
            'appointment_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('e.g., Monthly Checkup, Ultrasound Scan')
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Notes about this appointment'),
                'rows': 3
            }),
            'appointment_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'type': 'date'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'type': 'time'
            }),
            'doctor_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Doctor name')
            }),
            'hospital_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Hospital/Clinic name')
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'placeholder': _('Full address'),
                'rows': 2
            }),
        }