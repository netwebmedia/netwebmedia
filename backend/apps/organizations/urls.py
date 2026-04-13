from rest_framework.routers import DefaultRouter

from apps.organizations.views import OrganizationPresetViewSet, OrganizationViewSet


router = DefaultRouter()
router.register(r"presets", OrganizationPresetViewSet, basename="organization-preset")
router.register(r"", OrganizationViewSet, basename="organization")

urlpatterns = router.urls
