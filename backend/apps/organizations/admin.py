from django.contrib import admin

from apps.organizations.models import Membership, Organization, OrganizationPreset


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "business_type", "primary_email", "is_active")
    search_fields = ("name", "slug", "primary_email", "website")
    list_filter = ("business_type", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "role", "is_default", "is_active")
    search_fields = ("organization__name", "user__email", "user__username")
    list_filter = ("role", "is_default", "is_active")


@admin.register(OrganizationPreset)
class OrganizationPresetAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "business_type", "is_system", "is_active")
    search_fields = ("name", "code", "description")
    list_filter = ("business_type", "is_system", "is_active")
