DEFAULT_ORGANIZATION_PRESETS = [
    {
        "code": "agency-growth",
        "name": "Agency Growth CRM",
        "business_type": "agency",
        "description": "Prebuilt pipeline for inbound leads, retained service deals, and onboarding handoff.",
        "pipeline_blueprint": [
            {
                "name": "Inbound Leads",
                "entity_type": "lead",
                "stages": [
                    {"name": "New Inquiry", "probability": 10},
                    {"name": "Discovery Booked", "probability": 25},
                    {"name": "Qualified", "probability": 45},
                    {"name": "Proposal Sent", "probability": 70},
                    {"name": "Won", "probability": 100},
                    {"name": "Lost", "probability": 0},
                ],
            },
            {
                "name": "Service Deals",
                "entity_type": "deal",
                "stages": [
                    {"name": "Scoping", "probability": 20},
                    {"name": "Proposal Review", "probability": 55},
                    {"name": "Negotiation", "probability": 75},
                    {"name": "Closed Won", "probability": 100},
                    {"name": "Closed Lost", "probability": 0},
                ],
            },
        ],
        "custom_fields_blueprint": [
            {"entity_type": "lead", "name": "service_interest", "label": "Service Interest", "field_type": "select", "options": ["SEO", "Paid Media", "CRM", "Web Build", "Automation"]},
            {"entity_type": "lead", "name": "monthly_budget", "label": "Monthly Budget", "field_type": "currency"},
        ],
        "automation_blueprint": [
            {"name": "Assign discovery owner", "trigger": "lead.created"},
            {"name": "Proposal follow-up reminder", "trigger": "deal.stage_changed"},
        ],
    },
    {
        "code": "saas-revenue",
        "name": "SaaS Revenue CRM",
        "business_type": "saas",
        "description": "Built for trial, demo, and sales-assisted B2B SaaS funnels.",
        "pipeline_blueprint": [
            {
                "name": "Demo Requests",
                "entity_type": "lead",
                "stages": [
                    {"name": "New Demo", "probability": 15},
                    {"name": "Qualified Demo", "probability": 35},
                    {"name": "Solution Fit", "probability": 60},
                    {"name": "Trial / Pilot", "probability": 80},
                    {"name": "Closed Won", "probability": 100},
                    {"name": "Closed Lost", "probability": 0},
                ],
            }
        ],
        "custom_fields_blueprint": [
            {"entity_type": "company", "name": "crm_stack", "label": "CRM Stack", "field_type": "text"},
            {"entity_type": "lead", "name": "team_size", "label": "Team Size", "field_type": "number"},
        ],
        "automation_blueprint": [
            {"name": "Trial activation task", "trigger": "lead.stage_changed"},
            {"name": "Renewal health review", "trigger": "deal.created"},
        ],
    },
    {
        "code": "real-estate-intake",
        "name": "Real Estate Intake CRM",
        "business_type": "real_estate",
        "description": "Designed for buyer, seller, and investor lead qualification.",
        "pipeline_blueprint": [
            {
                "name": "Property Leads",
                "entity_type": "lead",
                "stages": [
                    {"name": "New Lead", "probability": 10},
                    {"name": "Contacted", "probability": 30},
                    {"name": "Qualified", "probability": 50},
                    {"name": "Viewing Scheduled", "probability": 70},
                    {"name": "Offer / Listing", "probability": 90},
                    {"name": "Closed", "probability": 100},
                ],
            }
        ],
        "custom_fields_blueprint": [
            {"entity_type": "lead", "name": "property_type", "label": "Property Type", "field_type": "select", "options": ["Residential", "Commercial", "Land", "Rental"]},
            {"entity_type": "lead", "name": "budget_range", "label": "Budget Range", "field_type": "text"},
        ],
        "automation_blueprint": [
            {"name": "Showing confirmation", "trigger": "task.created"},
        ],
    },
]
