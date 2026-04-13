from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from rest_framework import permissions, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.common.permissions import IsOrganizationMember, IsOrganizationViewer
from apps.organizations.models import Membership, Organization


class OrganizationContextMixin:
    organization_kwarg = "organization_slug"
    organization_query_param = "organization"
    organization_header = "X-Organization-Slug"

    def get_memberships(self):
        user = self.request.user
        return Membership.objects.select_related("organization").filter(
            user=user,
            is_active=True,
            organization__is_active=True,
        )

    def get_organization_slug(self):
        slug = self.kwargs.get(self.organization_kwarg)
        if slug:
            return slug

        slug = self.request.headers.get(self.organization_header)
        if slug:
            return slug

        slug = self.request.query_params.get(self.organization_query_param)
        if slug:
            return slug

        if isinstance(self.request.data, dict):
            return self.request.data.get("organization_slug")

        return None

    def get_organization(self):
        if hasattr(self.request, "_cached_organization"):
            return self.request._cached_organization

        memberships = self.get_memberships()
        if not memberships.exists():
            raise PermissionDenied("You do not belong to any active organization.")

        slug = self.get_organization_slug()
        membership = None
        if slug:
            membership = memberships.filter(organization__slug=slug).first()
            if membership is None:
                raise NotFound("Organization not found for the current user.")
        else:
            membership = memberships.order_by("-is_default", "organization__name").first()

        self.request._cached_organization = membership.organization
        self.request._cached_membership = membership

        # Set RLS session variable immediately when organization is resolved
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('app.current_organization_id', %s, TRUE)",
                    [str(membership.organization.pk)],
                )

        return membership.organization

    def get_membership(self):
        if hasattr(self.request, "_cached_membership"):
            return self.request._cached_membership

        self.get_organization()
        return self.request._cached_membership


class OrganizationScopedViewSet(OrganizationContextMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationViewer]
    organization_field = "organization"

    def initial(self, request, *args, **kwargs):
        """Resolve organization before permission checks so membership is cached."""
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        # Ensure organization (and thus RLS var) is resolved before any query
        org = self.get_organization()
        queryset = super().get_queryset()
        if not hasattr(queryset.model, self.organization_field):
            raise ImproperlyConfigured(
                f"{queryset.model.__name__} does not define `{self.organization_field}`."
            )
        return queryset.filter(**{self.organization_field: org})

    def perform_create(self, serializer):
        serializer.save(**{self.organization_field: self.get_organization()})
