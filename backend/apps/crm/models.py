from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BaseModel
from apps.organizations.models import Organization


class OrganizationBoundModel(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Company(OrganizationBoundModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PROSPECT = "prospect", "Prospect"
        CUSTOMER = "customer", "Customer"
        PARTNER = "partner", "Partner"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    company_size = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PROSPECT)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_companies",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("name",)
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class Contact(OrganizationBoundModel):
    class LifecycleStage(models.TextChoices):
        LEAD = "lead", "Lead"
        MQL = "mql", "Marketing Qualified"
        SQL = "sql", "Sales Qualified"
        CUSTOMER = "customer", "Customer"
        EVANGELIST = "evangelist", "Evangelist"

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    lifecycle_stage = models.CharField(
        max_length=24,
        choices=LifecycleStage.choices,
        default=LifecycleStage.LEAD,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_contacts",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("first_name", "last_name")

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email or str(self.id)


class Pipeline(OrganizationBoundModel):
    class EntityType(models.TextChoices):
        LEAD = "lead", "Lead"
        DEAL = "deal", "Deal"

    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=24, choices=EntityType.choices)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("entity_type", "name")
        unique_together = ("organization", "name", "entity_type")

    def __str__(self):
        return f"{self.name} ({self.entity_type})"


class PipelineStage(OrganizationBoundModel):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)
    probability = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("pipeline", "order", "name")
        unique_together = ("pipeline", "name")

    def __str__(self):
        return f"{self.pipeline.name}: {self.name}"


class Lead(OrganizationBoundModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        QUALIFIED = "qualified", "Qualified"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    title = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
        limit_choices_to={"entity_type": Pipeline.EntityType.LEAD},
    )
    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    source = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN)
    score = models.PositiveIntegerField(default=0)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_leads",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )
    description = models.TextField(blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    next_step_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class Deal(OrganizationBoundModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        WON = "won", "Won"
        LOST = "lost", "Lost"
        STALLED = "stalled", "Stalled"

    name = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )
    primary_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
        limit_choices_to={"entity_type": Pipeline.EntityType.DEAL},
    )
    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_close_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_deals",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_deals",
    )
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Task(OrganizationBoundModel):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        BLOCKED = "blocked", "Blocked"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=24, choices=Priority.choices, default=Priority.MEDIUM)
    due_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_tasks",
    )
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="tasks")
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE, related_name="tasks")
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="tasks")
    deal = models.ForeignKey(Deal, null=True, blank=True, on_delete=models.CASCADE, related_name="tasks")

    class Meta:
        ordering = ("due_at", "-created_at")

    def __str__(self):
        return self.title


class Note(OrganizationBoundModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_notes",
    )
    body = models.TextField()
    pinned = models.BooleanField(default=False)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="notes")
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE, related_name="notes")
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="notes")
    deal = models.ForeignKey(Deal, null=True, blank=True, on_delete=models.CASCADE, related_name="notes")

    class Meta:
        ordering = ("-pinned", "-created_at")

    def __str__(self):
        return f"Note {self.id}"


class Activity(OrganizationBoundModel):
    class Kind(models.TextChoices):
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        MEETING = "meeting", "Meeting"
        STATUS_CHANGE = "status_change", "Status Change"
        COMMENT = "comment", "Comment"
        SYSTEM = "system", "System"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_activities",
    )
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.SYSTEM)
    summary = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    occurred_at = models.DateTimeField()
    payload = models.JSONField(default=dict, blank=True)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="activities")
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE, related_name="activities")
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="activities")
    deal = models.ForeignKey(Deal, null=True, blank=True, on_delete=models.CASCADE, related_name="activities")

    class Meta:
        ordering = ("-occurred_at",)

    def __str__(self):
        return self.summary


class CustomFieldDefinition(OrganizationBoundModel):
    class EntityType(models.TextChoices):
        COMPANY = "company", "Company"
        CONTACT = "contact", "Contact"
        LEAD = "lead", "Lead"
        DEAL = "deal", "Deal"

    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        TEXTAREA = "textarea", "Textarea"
        NUMBER = "number", "Number"
        CURRENCY = "currency", "Currency"
        DATE = "date", "Date"
        BOOLEAN = "boolean", "Boolean"
        SELECT = "select", "Select"
        MULTISELECT = "multiselect", "Multi Select"

    entity_type = models.CharField(max_length=24, choices=EntityType.choices)
    name = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    field_type = models.CharField(max_length=24, choices=FieldType.choices)
    help_text = models.CharField(max_length=255, blank=True)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    options = models.JSONField(default=list, blank=True)
    default_value = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("entity_type", "label")
        unique_together = ("organization", "entity_type", "name")

    def __str__(self):
        return f"{self.entity_type}: {self.label}"


class CustomFieldValue(OrganizationBoundModel):
    definition = models.ForeignKey(
        CustomFieldDefinition,
        on_delete=models.CASCADE,
        related_name="values",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    value = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("definition__label",)
        unique_together = ("definition", "content_type", "object_id")

    def __str__(self):
        return f"{self.definition.label} value"
