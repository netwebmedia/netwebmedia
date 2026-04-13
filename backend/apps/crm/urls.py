from rest_framework.routers import DefaultRouter

from apps.crm.views import (
    ActivityViewSet,
    CompanyViewSet,
    ContactViewSet,
    CustomFieldDefinitionViewSet,
    CustomFieldValueViewSet,
    DealViewSet,
    LeadViewSet,
    NoteViewSet,
    PipelineStageViewSet,
    PipelineViewSet,
    TaskViewSet,
)


router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"pipelines", PipelineViewSet, basename="pipeline")
router.register(r"pipeline-stages", PipelineStageViewSet, basename="pipeline-stage")
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"deals", DealViewSet, basename="deal")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"activities", ActivityViewSet, basename="activity")
router.register(r"custom-fields", CustomFieldDefinitionViewSet, basename="custom-field")
router.register(r"custom-values", CustomFieldValueViewSet, basename="custom-value")

urlpatterns = router.urls
