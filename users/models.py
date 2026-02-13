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
    """
    
    # --- CHOICES ---
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say')),
    ]
    
    AVATAR_CHOICES = [
        ('avatar1', 'Avatar 1'),
        ('avatar2', 'Avatar 2'),
        ('avatar3', 'Avatar 3'),
        ('male', 'Male Default'),
        ('female', 'Female Default'),
    ]

    PREGNANCY_STATUS_CHOICES = [
        ('not_pregnant', _('Not Pregnant')),
        ('pregnant', _('Pregnant')),
        ('postpartum', _('Postpartum')),
        ('not_applicable', _('Not Applicable')),
    ]
    
    # --- FIELDS ---
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Avatar Selection
    avatar = models.CharField(
        max_length=20,
        choices=AVATAR_CHOICES,
        default='avatar1',
        blank=True,
        null=True
    )
    
    # Uploaded Picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    # Demographics
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        null=True, blank=True
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    
    # Metrics
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Maternal Health
    pregnancy_status = models.CharField(max_length=20, choices=PREGNANCY_STATUS_CHOICES, default='not_applicable')
    pregnancy_weeks = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(42)])
    due_date = models.DateField(null=True, blank=True)
    number_of_children = models.PositiveIntegerField(default=0)
    
    # Settings (RESTORED THESE FIELDS)
    preferred_language = models.CharField(max_length=5, default='en')
    dark_mode_enabled = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Metadata
    profile_completed = models.BooleanField(default=False)
    medical_disclaimer_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def display_profile_image(self):
        """Logic: Return Uploaded Image -> OR Selected Avatar -> OR Default."""
        if self.profile_picture:
            return self.profile_picture.url
        if self.avatar:
            return f"/static/avatars/{self.avatar}.png"
        return "/static/avatars/default.png"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize uploaded image if it exists
        if self.profile_picture:
            try:
                img_path = self.profile_picture.path
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    if img.height > 400 or img.width > 400:
                        output_size = (400, 400)
                        img.thumbnail(output_size)
                        img.save(img_path)
            except Exception:
                pass
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