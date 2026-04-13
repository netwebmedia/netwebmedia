from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import BaseModel


class Organization(BaseModel):
    class BusinessType(models.TextChoices):
        AGENCY = "agency", "Agency"
        SAAS = "saas", "SaaS"
        SERVICES = "services", "Professional Services"
        ECOMMERCE = "ecommerce", "E-commerce"
        HEALTHCARE = "healthcare", "Healthcare"
        EDUCATION = "education", "Education"
        REAL_ESTATE = "real_estate", "Real Estate"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    legal_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(
        max_length=32,
        choices=BusinessType.choices,
        default=BusinessType.SERVICES,
    )
    website = models.URLField(blank=True)
    primary_email = models.EmailField(blank=True)
    primary_phone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=80, blank=True)
    timezone = models.CharField(max_length=64, default="America/Santiago")
    currency = models.CharField(max_length=8, default="USD")
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Membership(BaseModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        SALES = "sales", "Sales"
        MARKETING = "marketing", "Marketing"
        OPERATIONS = "operations", "Operations"
        VIEWER = "viewer", "Viewer"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=24, choices=Role.choices, default=Role.VIEWER)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")
        ordering = ("organization__name", "user__email")

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"


class OrganizationPreset(BaseModel):
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=255)
    business_type = models.CharField(
        max_length=32,
        choices=Organization.BusinessType.choices,
        default=Organization.BusinessType.OTHER,
    )
    description = models.TextField()
    pipeline_blueprint = models.JSONField(default=list, blank=True)
    custom_fields_blueprint = models.JSONField(default=list, blank=True)
    automation_blueprint = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
