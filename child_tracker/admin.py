from django.contrib import admin
from .models import Child, VaccineSchedule, VaccinationRecord, GrowthRecord, Milestone

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'age_display', 'gender')

@admin.register(VaccineSchedule)
class VaccineScheduleAdmin(admin.ModelAdmin):
    list_display = ('vaccine_name', 'age_in_months', 'is_mandatory')
    ordering = ('age_in_months',)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'typical_age_months')
    list_filter = ('category',)

# Register other models as needed
admin.site.register(VaccinationRecord)
admin.site.register(GrowthRecord)