"""
Forms for user authentication and profile management.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
from datetime import date


class UserRegisterForm(UserCreationForm):
    """Enhanced registration form with email validation"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Email address')
        })
    )
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('First name')
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Last name (optional)')
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Tailwind classes to all fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Username')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Confirm password')
        })
    
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already registered.'))
        return email


class UserLoginForm(AuthenticationForm):
    """Styled login form"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Username or Email')
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300',
            'placeholder': _('Password')
        })


class ProfileSetupForm(forms.ModelForm):
    """
    Post-registration profile setup form.
    Captures critical data for RAG context.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'age', 'gender', 'height', 'weight', 'profession', 'location',
            'pregnancy_status', 'pregnancy_weeks', 'due_date', 'number_of_children',
            'profile_picture', 'preferred_language'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Age in years'),
                'min': 1,
                'max': 120
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Height in cm'),
                'step': '0.01'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Weight in kg'),
                'step': '0.01'
            }),
            'profession': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Your profession')
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('City, State')
            }),
            'pregnancy_status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200'
            }),
            'pregnancy_weeks': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Current week (0-42)'),
                'min': 0,
                'max': 42
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'type': 'date'
            }),
            'number_of_children': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200',
                'placeholder': _('Number of children'),
                'min': 0
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500',
                'accept': 'image/*'
            }),
            'preferred_language': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200'
            }),
        }
    
    def clean_pregnancy_weeks(self):
        """Validate pregnancy weeks based on pregnancy status"""
        status = self.cleaned_data.get('pregnancy_status')
        weeks = self.cleaned_data.get('pregnancy_weeks')
        
        if status == 'pregnant' and weeks is None:
            raise forms.ValidationError(_('Please specify how many weeks pregnant you are.'))
        
        return weeks
    
    def clean_due_date(self):
        """Ensure due date is in the future"""
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():
            raise forms.ValidationError(_('Due date must be in the future.'))
        return due_date


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating existing profiles"""
    
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'age', 'gender', 'height', 'weight', 'profession', 'location',
            'pregnancy_status', 'pregnancy_weeks', 'due_date', 'number_of_children',
            'profile_picture', 'preferred_language', 'dark_mode_enabled', 'email_notifications'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'profession': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'pregnancy_status': forms.Select(attrs={'class': 'form-select'}),
            'pregnancy_weeks': forms.NumberInput(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'number_of_children': forms.NumberInput(attrs={'class': 'form-input'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'dark_mode_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name