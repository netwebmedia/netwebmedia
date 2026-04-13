from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.accounts.models import User
from apps.organizations.models import Membership, Organization, OrganizationPreset
from apps.organizations.services import apply_preset_to_organization, seed_system_presets


class Command(BaseCommand):
    help = "Create an organization, owner membership, and optional CRM preset in one step."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Organization name")
        parser.add_argument("--owner-email", required=True, help="Owner email")
        parser.add_argument("--preset", help="Preset code to apply")
        parser.add_argument("--slug", help="Optional organization slug")
        parser.add_argument("--business-type", default=Organization.BusinessType.SERVICES)

    def handle(self, *args, **options):
        seed_system_presets()

        name = options["name"]
        slug = options["slug"] or slugify(name)
        owner_email = options["owner_email"]
        business_type = options["business_type"]
        preset_code = options.get("preset")

        if business_type not in Organization.BusinessType.values:
            raise CommandError("Invalid business type.")

        organization, created = Organization.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "business_type": business_type,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created organization `{organization.name}`."))
        else:
            self.stdout.write(self.style.WARNING(f"Organization `{organization.name}` already existed."))

        user, user_created = User.objects.get_or_create(
            email=owner_email,
            defaults={
                "username": owner_email,
                "first_name": name,
                "is_active": True,
            },
        )
        if user_created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created owner user `{owner_email}` with unusable password."))

        Membership.objects.update_or_create(
            organization=organization,
            user=user,
            defaults={"role": Membership.Role.OWNER, "is_default": True, "is_active": True},
        )

        if preset_code:
            try:
                preset = OrganizationPreset.objects.get(code=preset_code)
            except OrganizationPreset.DoesNotExist as exc:
                raise CommandError(f"Preset `{preset_code}` does not exist.") from exc

            apply_preset_to_organization(organization, preset)
            self.stdout.write(self.style.SUCCESS(f"Applied preset `{preset.code}` to `{organization.slug}`."))
