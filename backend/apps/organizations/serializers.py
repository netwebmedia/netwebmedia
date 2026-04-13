from rest_framework import serializers

from apps.organizations.models import Membership, Organization, OrganizationPreset


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "legal_name",
            "business_type",
            "website",
            "primary_email",
            "primary_phone",
            "country",
            "timezone",
            "currency",
            "settings",
            "metadata",
        )


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Membership
        fields = (
            "id",
            "organization",
            "user",
            "user_email",
            "user_name",
            "role",
            "is_default",
            "is_active",
            "joined_at",
        )


class OrganizationPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationPreset
        fields = (
            "id",
            "code",
            "name",
            "business_type",
            "description",
            "pipeline_blueprint",
            "custom_fields_blueprint",
            "automation_blueprint",
        )
