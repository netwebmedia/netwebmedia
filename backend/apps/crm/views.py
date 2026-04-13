from django.utils import timezone
from rest_framework import permissions

from apps.common.permissions import (
    IsOrganizationAdmin,
    IsOrganizationManager,
    IsOrganizationViewer,
    IsOwnerOrReadOnly,
)
from apps.common.views import OrganizationScopedViewSet
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
from apps.crm.serializers import (
    ActivitySerializer,
    CompanySerializer,
    ContactSerializer,
    CustomFieldDefinitionSerializer,
    CustomFieldValueSerializer,
    DealSerializer,
    LeadSerializer,
    NoteSerializer,
    PipelineSerializer,
    PipelineStageSerializer,
    TaskSerializer,
)


class CompanyViewSet(OrganizationScopedViewSet):
    queryset = Company.objects.select_related("organization", "owner")
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationViewer, IsOwnerOrReadOnly]
    search_fields = ("name", "website", "industry")
    ordering_fields = ("name", "created_at", "updated_at")


class ContactViewSet(OrganizationScopedViewSet):
    queryset = Contact.objects.select_related("organization", "company", "owner")
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationViewer, IsOwnerOrReadOnly]
    search_fields = ("first_name", "last_name", "email", "phone", "job_title")
    ordering_fields = ("first_name", "last_name", "created_at")


class PipelineViewSet(OrganizationScopedViewSet):
    queryset = Pipeline.objects.select_related("organization")
    serializer_class = PipelineSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationManager]
    search_fields = ("name", "entity_type")
    ordering_fields = ("name", "entity_type", "created_at")


class PipelineStageViewSet(OrganizationScopedViewSet):
    queryset = PipelineStage.objects.select_related("organization", "pipeline")
    serializer_class = PipelineStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationManager]
    search_fields = ("name", "pipeline__name")
    ordering_fields = ("order", "probability", "created_at")


class LeadViewSet(OrganizationScopedViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationViewer, IsOwnerOrReadOnly]
    queryset = Lead.objects.select_related(
        "organization",
        "company",
        "contact",
        "pipeline",
        "stage",
        "owner",
        "assigned_to",
    )
    serializer_class = LeadSerializer
    search_fields = ("title", "source", "company__name", "contact__email")
    ordering_fields = ("created_at", "updated_at", "score", "estimated_value")


class DealViewSet(OrganizationScopedViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationViewer, IsOwnerOrReadOnly]
    queryset = Deal.objects.select_related(
        "organization",
        "company",
        "primary_contact",
        "pipeline",
        "stage",
        "owner",
        "assigned_to",
    )
    serializer_class = DealSerializer
    search_fields = ("name", "company__name", "primary_contact__email")
    ordering_fields = ("created_at", "updated_at", "value", "expected_close_date")


class TaskViewSet(OrganizationScopedViewSet):
    queryset = Task.objects.select_related(
        "organization",
        "assigned_to",
        "company",
        "contact",
        "lead",
        "deal",
    )
    serializer_class = TaskSerializer
    search_fields = ("title", "description")
    ordering_fields = ("due_at", "created_at", "updated_at")


class NoteViewSet(OrganizationScopedViewSet):
    queryset = Note.objects.select_related("organization", "author", "company", "contact", "lead", "deal")
    serializer_class = NoteSerializer
    search_fields = ("body",)
    ordering_fields = ("created_at", "updated_at")

    def perform_create(self, serializer):
        serializer.save(
            organization=self.get_organization(),
            author=self.request.user,
        )


class ActivityViewSet(OrganizationScopedViewSet):
    queryset = Activity.objects.select_related("organization", "actor", "company", "contact", "lead", "deal")
    serializer_class = ActivitySerializer
    search_fields = ("summary", "details")
    ordering_fields = ("occurred_at", "created_at", "updated_at")

    def perform_create(self, serializer):
        serializer.save(
            organization=self.get_organization(),
            actor=self.request.user,
            occurred_at=serializer.validated_data.get("occurred_at", timezone.now()),
        )


class CustomFieldDefinitionViewSet(OrganizationScopedViewSet):
    queryset = CustomFieldDefinition.objects.select_related("organization")
    serializer_class = CustomFieldDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    search_fields = ("label", "name", "entity_type")
    ordering_fields = ("entity_type", "label", "created_at")


class CustomFieldValueViewSet(OrganizationScopedViewSet):
    queryset = CustomFieldValue.objects.select_related("organization", "definition", "content_type")
    serializer_class = CustomFieldValueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationViewer]
    search_fields = ("definition__label", "definition__name")
    ordering_fields = ("created_at", "updated_at")
