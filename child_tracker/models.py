"""
Child Health Tracker models - Vaccines, Medications, Growth Milestones.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta


class Child(models.Model):
    """
    Child profile linked to parent user.
    """
    
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]
    
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    birth_weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Birth weight in kg")
    )
    birth_height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Birth height in cm")
    )
    blood_group = models.CharField(max_length=5, blank=True, help_text=_("e.g., O+, A-, AB+"))
    
    # Medical
    allergies = models.TextField(blank=True, help_text=_("Known allergies, separated by commas"))
    medical_conditions = models.TextField(blank=True, help_text=_("Any chronic conditions"))
    
    # Photo
    photo = models.ImageField(upload_to='child_photos/', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Child")
        verbose_name_plural = _("Children")
        ordering = ['date_of_birth']
    
    def __str__(self):
        return f"{self.name} ({self.parent.username})"
    
    @property
    def age_months(self):
        """Calculate age in months"""
        today = date.today()
        months = (today.year - self.date_of_birth.year) * 12
        months += today.month - self.date_of_birth.month
        return months
    
    @property
    def age_display(self):
        """Human-readable age"""
        months = self.age_months
        if months < 12:
            return f"{months} {_('months')}"
        years = months // 12
        remaining_months = months % 12
        if remaining_months == 0:
            return f"{years} {_('years')}"
        return f"{years} {_('years')} {remaining_months} {_('months')}"


class VaccineSchedule(models.Model):
    """
    Standard vaccine schedule template (as per Indian immunization program).
    """
    
    vaccine_name = models.CharField(max_length=100)
    description = models.TextField()
    age_in_months = models.PositiveIntegerField(help_text=_("Age when vaccine should be given"))
    dose_number = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    
    # Information
    protects_against = models.CharField(max_length=200, blank=True)
    side_effects = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("Vaccine Schedule")
        verbose_name_plural = _("Vaccine Schedules")
        ordering = ['age_in_months', 'dose_number']
    
    def __str__(self):
        return f"{self.vaccine_name} (Dose {self.dose_number}) - {self.age_in_months} months"


class VaccinationRecord(models.Model):
    """
    Individual vaccination records for each child.
    """
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine = models.ForeignKey(VaccineSchedule, on_delete=models.CASCADE)
    
    # Administration details
    administered_date = models.DateField(null=True, blank=True)
    administered_by = models.CharField(max_length=100, blank=True, help_text=_("Doctor/Clinic name"))
    batch_number = models.CharField(max_length=50, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    is_overdue = models.BooleanField(default=False)
    
    # Reactions
    had_reaction = models.BooleanField(default=False)
    reaction_details = models.TextField(blank=True)
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Vaccination Record")
        verbose_name_plural = _("Vaccination Records")
        unique_together = ['child', 'vaccine']
        ordering = ['vaccine__age_in_months']
    
    def __str__(self):
        return f"{self.child.name} - {self.vaccine.vaccine_name}"
    
    @property
    def is_due(self):
        """Check if vaccine is due based on child's age"""
        if self.is_completed:
            return False
        child_age_months = self.child.age_months
        return child_age_months >= self.vaccine.age_in_months
    
    @property
    def days_until_due(self):
        """Calculate days until vaccine is due"""
        child_dob = self.child.date_of_birth
        due_date = child_dob + timedelta(days=self.vaccine.age_in_months * 30)
        return (due_date - date.today()).days


class GrowthRecord(models.Model):
    """
    Track child's growth over time.
    """
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='growth_records')
    
    # Measurements
    date = models.DateField(default=date.today)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Weight in kg"))
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Height in cm"))
    head_circumference = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Head circumference in cm (for infants)")
    )
    
    # Context
    notes = models.TextField(blank=True)
    measured_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = _("Growth Record")
        verbose_name_plural = _("Growth Records")
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.child.name} - {self.date}"


class Medication(models.Model):
    """
    Track medications given to children.
    """
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='medications')
    
    # Medication details
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text=_("e.g., 5ml, 250mg"))
    frequency = models.CharField(max_length=100, help_text=_("e.g., Twice daily, Every 6 hours"))
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Purpose
    prescribed_for = models.CharField(max_length=200, help_text=_("Condition/Symptom"))
    prescribed_by = models.CharField(max_length=100, blank=True, help_text=_("Doctor name"))
    
    # Instructions
    instructions = models.TextField(blank=True, help_text=_("Special instructions"))
    side_effects_observed = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Medication")
        verbose_name_plural = _("Medications")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} for {self.child.name}"


class Milestone(models.Model):
    """
    Developmental milestones template.
    """
    
    CATEGORY_CHOICES = [
        ('motor', _('Motor Skills')),
        ('social', _('Social & Emotional')),
        ('language', _('Language & Communication')),
        ('cognitive', _('Cognitive')),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    typical_age_months = models.PositiveIntegerField(help_text=_("Typical age when achieved"))
    
    class Meta:
        verbose_name = _("Milestone")
        verbose_name_plural = _("Milestones")
        ordering = ['typical_age_months', 'category']
    
    def __str__(self):
        return f"{self.title} ({self.typical_age_months} months)"


class MilestoneRecord(models.Model):
    """
    Track when child achieves milestones.
    """
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='milestone_records')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    
    achieved = models.BooleanField(default=False)
    achieved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("Milestone Record")
        verbose_name_plural = _("Milestone Records")
        unique_together = ['child', 'milestone']
        ordering = ['milestone__typical_age_months']
    
    def __str__(self):
        status = "Achieved" if self.achieved else "Pending"
        return f"{self.child.name} - {self.milestone.title} ({status})"


class EmergencyContact(models.Model):
    """
    Emergency contacts for child's healthcare.
    """
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='emergency_contacts')
    
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, help_text=_("e.g., Pediatrician, Grandparent"))
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Priority
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("Emergency Contact")
        verbose_name_plural = _("Emergency Contacts")
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.relationship}) for {self.child.name}"