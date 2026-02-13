"""
Maternal Health models - Medical Records Vault & Documents.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import date


class MedicalRecord(models.Model):
    """
    Store medical records, ultrasounds, test results organized by trimester.
    """
    
    RECORD_TYPE_CHOICES = [
        ('ultrasound', _('Ultrasound/Sonography')),
        ('blood_test', _('Blood Test Results')),
        ('urine_test', _('Urine Test Results')),
        ('scan', _('Medical Scan (CT/MRI)')),
        ('prescription', _('Prescription')),
        ('report', _('Medical Report')),
        ('vaccination', _('Vaccination Record')),
        ('other', _('Other Document')),
    ]
    
    TRIMESTER_CHOICES = [
        (1, _('First Trimester (Weeks 1-13)')),
        (2, _('Second Trimester (Weeks 14-26)')),
        (3, _('Third Trimester (Weeks 27-40)')),
        (0, _('Pre-Pregnancy/Other')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    
    # Document Details
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200, help_text=_("e.g., 20-Week Anatomy Scan, Blood Test Week 12"))
    description = models.TextField(blank=True, help_text=_("Notes about this record"))
    
    # File Storage
    document = models.FileField(
        upload_to='medical_records/%Y/%m/',
        help_text=_("Upload PDF, image, or document (max 10MB)")
    )
    thumbnail = models.ImageField(
        upload_to='medical_records/thumbnails/',
        blank=True,
        null=True,
        help_text=_("Auto-generated for images")
    )
    
    # Categorization
    trimester = models.PositiveIntegerField(
        choices=TRIMESTER_CHOICES,
        default=1,
        help_text=_("Which trimester was this from?")
    )
    pregnancy_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(42)],
        help_text=_("Specific week if known")
    )
    record_date = models.DateField(
        default=date.today,
        help_text=_("Date of test/scan/visit")
    )
    
    # Medical Information
    doctor_name = models.CharField(max_length=100, blank=True, help_text=_("Doctor/Clinic name"))
    hospital_name = models.CharField(max_length=200, blank=True)
    
    # Key Findings (for quick reference)
    key_findings = models.TextField(
        blank=True,
        help_text=_("Important notes or results (e.g., 'Baby weight: 2.5kg, Heart rate: Normal')")
    )
    
    # Tags for searching
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Tags separated by commas (e.g., diabetes, blood pressure)")
    )
    
    # Organization
    is_important = models.BooleanField(
        default=False,
        help_text=_("Star important documents")
    )
    is_archived = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Medical Record")
        verbose_name_plural = _("Medical Records")
        ordering = ['-record_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-record_date']),
            models.Index(fields=['trimester', '-record_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.get_trimester_display()})"
    
    @property
    def file_extension(self):
        """Get file extension"""
        if self.document:
            return self.document.name.split('.')[-1].lower()
        return None
    
    @property
    def is_image(self):
        """Check if document is an image"""
        return self.file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    @property
    def is_pdf(self):
        """Check if document is PDF"""
        return self.file_extension == 'pdf'
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.document:
            return round(self.document.size / (1024 * 1024), 2)
        return 0


class UltrasoundImage(models.Model):
    """
    Special model for ultrasound images with baby details.
    Extends MedicalRecord with pregnancy-specific information.
    """
    
    medical_record = models.OneToOneField(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='ultrasound_details'
    )
    
    # Baby Measurements
    baby_weight_grams = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Estimated baby weight in grams")
    )
    baby_length_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Baby length in cm")
    )
    head_circumference_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Vital Signs
    heart_rate_bpm = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Baby's heart rate (beats per minute)")
    )
    
    # Baby Position & Gender
    baby_position = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("e.g., Head down, Breech")
    )
    gender_revealed = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=20,
        blank=True,
        choices=[('boy', _('Boy')), ('girl', _('Girl')), ('not_revealed', _('Not Revealed'))]
    )
    
    # Additional Notes
    amniotic_fluid_level = models.CharField(max_length=50, blank=True)
    placenta_position = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Ultrasound Detail")
        verbose_name_plural = _("Ultrasound Details")
    
    def __str__(self):
        return f"Ultrasound Details - {self.medical_record.title}"


class AppointmentReminder(models.Model):
    """
    Track upcoming medical appointments and reminders.
    """
    
    APPOINTMENT_TYPE_CHOICES = [
        ('checkup', _('Regular Checkup')),
        ('ultrasound', _('Ultrasound/Scan')),
        ('blood_test', _('Blood Test')),
        ('vaccination', _('Vaccination')),
        ('specialist', _('Specialist Consultation')),
        ('other', _('Other')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment Details
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Date & Time
    appointment_date = models.DateField()
    appointment_time = models.TimeField(null=True, blank=True)
    
    # Location
    doctor_name = models.CharField(max_length=100, blank=True)
    hospital_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    
    # Status
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text=_("Post-appointment notes"))
    
    # Link to medical record if uploaded after appointment
    related_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Appointment")
        verbose_name_plural = _("Appointments")
        ordering = ['appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.title} on {self.appointment_date}"
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future"""
        return self.appointment_date >= date.today() and not self.is_completed
    
    @property
    def is_overdue(self):
        """Check if appointment was missed"""
        return self.appointment_date < date.today() and not self.is_completed