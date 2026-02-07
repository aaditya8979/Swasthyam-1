"""
User models for Swasthyam.
Extends Django's default User model with health-specific data.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os


class UserProfile(models.Model):
    """
    Extended user profile with health tracking data.
    This is the CORE model that enables context-aware AI responses.
    """
    
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say')),
    ]
    
    PREGNANCY_STATUS_CHOICES = [
        ('not_pregnant', _('Not Pregnant')),
        ('pregnant', _('Pregnant')),
        ('postpartum', _('Postpartum')),
        ('not_applicable', _('Not Applicable')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Demographics
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        null=True,
        blank=True,
        help_text=_("Age in years")
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    
    # Physical Metrics
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Height in centimeters")
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Weight in kilograms")
    )
    
    # Professional & Lifestyle
    profession = models.CharField(max_length=100, blank=True, help_text=_("Occupation"))
    location = models.CharField(max_length=100, blank=True, help_text=_("City, State"))
    
    # Maternal Health Specific
    pregnancy_status = models.CharField(
        max_length=20,
        choices=PREGNANCY_STATUS_CHOICES,
        default='not_applicable'
    )
    pregnancy_weeks = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(42)],
        help_text=_("Current week of pregnancy (0-42)")
    )
    due_date = models.DateField(null=True, blank=True, help_text=_("Expected delivery date"))
    
    # Children Information (for Child Tracker)
    number_of_children = models.PositiveIntegerField(default=0)
    
    # Profile Picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default.png',
        blank=True
    )
    
    # Preferences
    preferred_language = models.CharField(max_length=5, default='en', choices=[('en', 'English'), ('hi', 'Hindi')])
    dark_mode_enabled = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Medical Disclaimers
    accepted_terms = models.BooleanField(default=False)
    medical_disclaimer_accepted = models.BooleanField(default=False)
    
    # Metadata
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        """Return user's full name or username"""
        return self.user.get_full_name() or self.user.username
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 2)
        return None
    
    @property
    def bmi_category(self):
        """Return BMI category"""
        bmi = self.bmi
        if not bmi:
            return None
        if bmi < 18.5:
            return _("Underweight")
        elif 18.5 <= bmi < 25:
            return _("Normal weight")
        elif 25 <= bmi < 30:
            return _("Overweight")
        else:
            return _("Obese")
    
    @property
    def pregnancy_trimester(self):
        """Return current trimester if pregnant"""
        if self.pregnancy_status == 'pregnant' and self.pregnancy_weeks:
            if self.pregnancy_weeks <= 13:
                return 1
            elif self.pregnancy_weeks <= 26:
                return 2
            else:
                return 3
        return None
    
    @property
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            self.age, self.gender, self.height, self.weight,
            self.profession, self.location, self.profile_picture.name != 'profile_pictures/default.png'
        ]
        filled = sum(1 for field in fields if field)
        return round((filled / len(fields)) * 100)
    
    def save(self, *args, **kwargs):
        """Override save to resize profile pictures"""
        super().save(*args, **kwargs)
        
        # Resize profile picture to save space
        if self.profile_picture and os.path.exists(self.profile_picture.path):
            img = Image.open(self.profile_picture.path)
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize if larger than 400x400
            if img.height > 400 or img.width > 400:
                output_size = (400, 400)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)
                img.save(self.profile_picture.path, quality=85, optimize=True)


class ChatHistory(models.Model):
    """
    Store chat history for the RAG chatbot.
    Enables users to review past conversations and improves context.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_history')
    question = models.TextField(help_text=_("User's question"))
    answer = models.TextField(help_text=_("AI's response"))
    
    # Context at the time of the chat
    user_age_at_time = models.PositiveIntegerField(null=True, blank=True)
    pregnancy_weeks_at_time = models.PositiveIntegerField(null=True, blank=True)
    
    # Feedback
    helpful = models.BooleanField(null=True, blank=True, help_text=_("Was this response helpful?"))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=50, blank=True, help_text=_("Group chats by session"))
    
    class Meta:
        verbose_name = _("Chat History")
        verbose_name_plural = _("Chat Histories")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class MedicalDisclaimer(models.Model):
    """
    Track user acceptance of medical disclaimers.
    Required for legal compliance.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disclaimers')
    disclaimer_text = models.TextField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Medical Disclaimer")
        verbose_name_plural = _("Medical Disclaimers")
    
    def __str__(self):
        return f"{self.user.username} - Accepted on {self.accepted_at}"