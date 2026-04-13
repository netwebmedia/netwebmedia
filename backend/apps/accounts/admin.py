from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "username", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("CRM Profile", {"fields": ("phone", "job_title", "preferred_timezone")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("CRM Profile", {"fields": ("email", "phone", "job_title", "preferred_timezone")}),
    )
