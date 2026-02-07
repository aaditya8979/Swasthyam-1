"""
Admin configuration for user management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, ChatHistory, MedicalDisclaimer


class UserProfileInline(admin.StackedInline):
    """Inline profile editing in user admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('age', 'gender', 'profile_picture')
        }),
        ('Physical Metrics', {
            'fields': ('height', 'weight')
        }),
        ('Professional', {
            'fields': ('profession', 'location')
        }),
        ('Maternal Health', {
            'fields': ('pregnancy_status', 'pregnancy_weeks', 'due_date', 'number_of_children')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'dark_mode_enabled', 'email_notifications')
        }),
        ('Status', {
            'fields': ('profile_completed', 'medical_disclaimer_accepted')
        }),
    )


class UserAdmin(BaseUserAdmin):
    """Extended user admin with profile"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile_completed', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__profile_completed', 'profile__pregnancy_status')
    
    def profile_completed(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.profile_completed
        return False
    profile_completed.boolean = True
    profile_completed.short_description = 'Profile Complete'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Standalone profile admin"""
    list_display = ('user', 'age', 'gender', 'pregnancy_status', 'bmi_display', 'profile_completion', 'created_at')
    list_filter = ('gender', 'pregnancy_status', 'profile_completed', 'preferred_language')
    search_fields = ('user__username', 'user__email', 'profession', 'location')
    readonly_fields = ('created_at', 'updated_at', 'bmi_display', 'profile_completion_display')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Demographics', {
            'fields': ('age', 'gender', 'profile_picture')
        }),
        ('Physical Metrics', {
            'fields': ('height', 'weight', 'bmi_display')
        }),
        ('Professional', {
            'fields': ('profession', 'location')
        }),
        ('Maternal Health', {
            'fields': ('pregnancy_status', 'pregnancy_weeks', 'due_date', 'number_of_children'),
            'description': 'Information specific to maternal health tracking'
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'dark_mode_enabled', 'email_notifications')
        }),
        ('Status', {
            'fields': ('profile_completed', 'medical_disclaimer_accepted', 'profile_completion_display')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def bmi_display(self, obj):
        bmi = obj.bmi
        if bmi:
            category = obj.bmi_category
            color = 'green' if 18.5 <= bmi < 25 else 'orange'
            return format_html(
                '<span style="color: {};">{:.2f} ({})</span>',
                color, bmi, category
            )
        return 'N/A'
    bmi_display.short_description = 'BMI'
    
    def profile_completion(self, obj):
        percentage = obj.profile_completion_percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color, percentage
        )
    profile_completion.short_description = 'Completion'
    
    def profile_completion_display(self, obj):
        percentage = obj.profile_completion_percentage
        return f"{percentage}%"
    profile_completion_display.short_description = 'Profile Completion'


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    """Admin for chat history"""
    list_display = ('user', 'question_preview', 'helpful', 'created_at', 'session_id')
    list_filter = ('helpful', 'created_at')
    search_fields = ('user__username', 'question', 'answer', 'session_id')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User & Session', {
            'fields': ('user', 'session_id')
        }),
        ('Conversation', {
            'fields': ('question', 'answer')
        }),
        ('Context', {
            'fields': ('user_age_at_time', 'pregnancy_weeks_at_time')
        }),
        ('Feedback', {
            'fields': ('helpful',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'


@admin.register(MedicalDisclaimer)
class MedicalDisclaimerAdmin(admin.ModelAdmin):
    """Admin for medical disclaimer tracking"""
    list_display = ('user', 'accepted_at', 'ip_address')
    list_filter = ('accepted_at',)
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('accepted_at',)
    date_hierarchy = 'accepted_at'


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)