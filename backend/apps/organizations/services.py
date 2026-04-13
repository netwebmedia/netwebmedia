from apps.crm.models import CustomFieldDefinition, Pipeline, PipelineStage
from apps.organizations.models import Organization, OrganizationPreset
from apps.organizations.presets import DEFAULT_ORGANIZATION_PRESETS


def seed_system_presets():
    created = []
    for preset_data in DEFAULT_ORGANIZATION_PRESETS:
        preset, _ = OrganizationPreset.objects.update_or_create(
            code=preset_data["code"],
            defaults=preset_data,
        )
        created.append(preset)
    return created


def apply_preset_to_organization(organization: Organization, preset: OrganizationPreset):
    for pipeline_data in preset.pipeline_blueprint:
        pipeline, _ = Pipeline.objects.get_or_create(
            organization=organization,
            name=pipeline_data["name"],
            entity_type=pipeline_data["entity_type"],
            defaults={"is_default": True},
        )
        for order, stage_data in enumerate(pipeline_data.get("stages", []), start=1):
            PipelineStage.objects.get_or_create(
                organization=organization,
                pipeline=pipeline,
                name=stage_data["name"],
                defaults={
                    "order": order,
                    "probability": stage_data.get("probability", 0),
                },
            )

    for field_data in preset.custom_fields_blueprint:
        options = field_data.get("options", [])
        CustomFieldDefinition.objects.get_or_create(
            organization=organization,
            entity_type=field_data["entity_type"],
            name=field_data["name"],
            defaults={
                "label": field_data["label"],
                "field_type": field_data["field_type"],
                "options": options,
            },
        )
