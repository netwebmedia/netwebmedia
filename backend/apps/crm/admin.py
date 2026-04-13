from django.contrib import admin

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


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status", "industry", "owner")
    search_fields = ("name", "website", "industry")
    list_filter = ("organization", "status")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "organization", "email", "lifecycle_stage", "owner")
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("organization", "lifecycle_stage")


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "entity_type", "is_default")
    search_fields = ("name",)
    list_filter = ("organization", "entity_type", "is_default")


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ("name", "pipeline", "order", "probability")
    search_fields = ("name", "pipeline__name")
    list_filter = ("organization", "pipeline")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "status", "source", "score", "assigned_to")
    search_fields = ("title", "source", "company__name", "contact__email")
    list_filter = ("organization", "status", "source")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status", "value", "expected_close_date", "assigned_to")
    search_fields = ("name", "company__name", "primary_contact__email")
    list_filter = ("organization", "status")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "status", "priority", "due_at", "assigned_to")
    search_fields = ("title", "description")
    list_filter = ("organization", "status", "priority")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "author", "pinned", "created_at")
    search_fields = ("body",)
    list_filter = ("organization", "pinned")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("summary", "organization", "kind", "actor", "occurred_at")
    search_fields = ("summary", "details")
    list_filter = ("organization", "kind")


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ("label", "organization", "entity_type", "field_type", "is_required", "is_active")
    search_fields = ("label", "name")
    list_filter = ("organization", "entity_type", "field_type", "is_active")


@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ("definition", "organization", "content_type", "object_id")
    search_fields = ("definition__label",)
    list_filter = ("organization", "content_type")
