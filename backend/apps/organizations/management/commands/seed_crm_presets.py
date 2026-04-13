from django.core.management.base import BaseCommand

from apps.organizations.services import seed_system_presets


class Command(BaseCommand):
    help = "Seed default NetWebMedia CRM presets for different business types."

    def handle(self, *args, **options):
        presets = seed_system_presets()
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(presets)} CRM presets."))
