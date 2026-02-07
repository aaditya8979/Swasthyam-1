from django import forms
from .models import Child, GrowthRecord, Medication, EmergencyContact, VaccinationRecord

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'gender', 'date_of_birth', 'blood_group', 'allergies', 'medical_conditions', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Child\'s Name'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'type': 'date'}),
            'blood_group': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'e.g. O+'}),
            'allergies': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg h-20', 'placeholder': 'Peanuts, Dust, etc.'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg h-20', 'placeholder': 'Asthma, etc.'}),
        }

class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['date', 'weight', 'height', 'head_circumference', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'type': 'date'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'step': '0.01', 'placeholder': 'kg'}),
            'height': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'step': '0.01', 'placeholder': 'cm'}),
            'head_circumference': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'step': '0.01', 'placeholder': 'cm'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg h-20'}),
        }

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'frequency', 'start_date', 'end_date', 'prescribed_for', 'instructions']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'instructions': forms.Textarea(attrs={'class': 'form-input h-20'}),
        }

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone', 'is_primary']