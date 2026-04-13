from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.organizations.models import Membership, Organization, OrganizationPreset
from apps.organizations.serializers import (
    MembershipSerializer,
    OrganizationPresetSerializer,
    OrganizationSerializer,
)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationSerializer
    search_fields = ("name", "slug", "primary_email")

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True,
        ).distinct()

    @action(detail=True, methods=["get"])
    def memberships(self, request, pk=None):
        organization = self.get_object()
        memberships = Membership.objects.filter(organization=organization, is_active=True).select_related("user")
        serializer = MembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class OrganizationPresetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationPresetSerializer
    queryset = OrganizationPreset.objects.filter(is_active=True)
    search_fields = ("name", "code", "description")
