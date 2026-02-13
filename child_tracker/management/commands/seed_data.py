from django.core.management.base import BaseCommand
from child_tracker.models import VaccineSchedule, Milestone

class Command(BaseCommand):
    help = 'Populates Vaccine Schedules and Milestones'

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Seeding Data...")

        # 1. Vaccine Schedule (Indian Immunization Schedule)
        vaccines = [
            ("BCG", "Tuberculosis", 0), # 0 months = birth
            ("Hepatitis B (Birth)", "Hepatitis B", 0),
            ("OPV-0", "Polio", 0),
            ("Pentavalent-1", "DPT + HepB + Hib", 1), # 6 weeks ~ 1.5 months
            ("Rotavirus-1", "Diarrhea", 1),
            ("Pentavalent-2", "DPT + HepB + Hib", 2), # 10 weeks ~ 2.5 months
            ("Pentavalent-3", "DPT + HepB + Hib", 3), # 14 weeks ~ 3.5 months
            ("Measles-1", "Measles", 9),
            ("Vitamin A", "Eye Health", 9),
            ("Booster DPT-1", "Diphtheria, Pertussis, Tetanus", 16),
        ]

        for name, desc, age in vaccines:
            VaccineSchedule.objects.get_or_create(
                vaccine_name=name,
                defaults={
                    'description': desc,
                    'age_in_months': age,
                    'is_mandatory': True
                }
            )
        self.stdout.write("✅ Vaccines Updated")

        # 2. Milestones (Developmental)
        milestones = [
            ("Social Smile", "social", 2),
            ("Holds Head Steady", "motor", 4),
            ("Rolls Over", "motor", 6),
            ("Responds to Name", "social", 7),
            ("Sits Without Support", "motor", 9),
            ("Says 'Mama'/'Dada'", "language", 12),
            ("Walks Alone", "motor", 15),
            ("Points to objects", "cognitive", 18),
        ]

        for title, cat, age in milestones:
            Milestone.objects.get_or_create(
                title=title,
                defaults={
                    'category': cat,
                    'description': f"Child should achieve {title}",
                    'typical_age_months': age
                }
            )
        self.stdout.write("✅ Milestones Updated")