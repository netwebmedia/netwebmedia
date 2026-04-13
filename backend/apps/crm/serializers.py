from rest_framework import serializers

from apps.crm.models import (
    Activity,
    Company,
    Contact,
    CustomFieldDefinition,
    CustomFieldValue,
    Deal,
    Lead,
    Note,
    Pipeline,
    PipelineStage,
    Task,
)


class OrganizationSlugMixin(serializers.ModelSerializer):
    organization_slug = serializers.SlugRelatedField(source="organization", slug_field="slug", read_only=True)


class CompanySerializer(OrganizationSlugMixin):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class ContactSerializer(OrganizationSlugMixin):
    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class PipelineSerializer(OrganizationSlugMixin):
    class Meta:
        model = Pipeline
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class PipelineStageSerializer(OrganizationSlugMixin):
    class Meta:
        model = PipelineStage
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class LeadSerializer(OrganizationSlugMixin):
    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class DealSerializer(OrganizationSlugMixin):
    class Meta:
        model = Deal
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class TaskSerializer(OrganizationSlugMixin):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class NoteSerializer(OrganizationSlugMixin):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "author", "created_at", "updated_at")


class ActivitySerializer(OrganizationSlugMixin):
    occurred_at = serializers.DateTimeField(required=False)

    class Meta:
        model = Activity
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "actor", "created_at", "updated_at")


class CustomFieldDefinitionSerializer(OrganizationSlugMixin):
    class Meta:
        model = CustomFieldDefinition
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")


class CustomFieldValueSerializer(OrganizationSlugMixin):
    class Meta:
        model = CustomFieldValue
        fields = "__all__"
        read_only_fields = ("organization", "organization_slug", "created_at", "updated_at")
