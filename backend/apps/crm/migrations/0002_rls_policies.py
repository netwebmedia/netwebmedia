"""
PostgreSQL Row-Level Security (RLS) policies for all organization-scoped tables.

Every CRM table gets an RLS policy that restricts SELECT, INSERT, UPDATE, DELETE
to rows whose organization_id matches the current session variable
`app.current_organization_id`.

Django sets this variable via the OrganizationRLSMiddleware before each request.

NOTE: RLS is only applied when using PostgreSQL. SQLite is silently skipped.
"""

from django.db import migrations

# All organization-scoped tables in the CRM app
RLS_TABLES = [
    "crm_company",
    "crm_contact",
    "crm_pipeline",
    "crm_pipelinestage",
    "crm_lead",
    "crm_deal",
    "crm_task",
    "crm_note",
    "crm_activity",
    "crm_customfielddefinition",
    "crm_customfieldvalue",
]

# Also protect org-level tables
ORG_TABLES = [
    "organizations_membership",
]


def enable_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    cursor = schema_editor.connection.cursor()

    # Create the helper function that reads the session variable
    cursor.execute("""
        CREATE OR REPLACE FUNCTION current_org_id()
        RETURNS uuid AS $$
        BEGIN
            RETURN NULLIF(current_setting('app.current_organization_id', TRUE), '')::uuid;
        EXCEPTION
            WHEN OTHERS THEN RETURN NULL;
        END;
        $$ LANGUAGE plpgsql STABLE;
    """)

    for table in RLS_TABLES:
        # Enable RLS on the table
        cursor.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

        # Force RLS even for table owners (superusers bypass by default)
        cursor.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")

        # Policy: rows visible only when organization_id matches session var
        cursor.execute(f"""
            CREATE POLICY org_isolation ON {table}
                USING (organization_id = current_org_id())
                WITH CHECK (organization_id = current_org_id());
        """)

    # Membership table: users can only see memberships for their current org
    for table in ORG_TABLES:
        cursor.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        cursor.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        cursor.execute(f"""
            CREATE POLICY org_isolation ON {table}
                USING (organization_id = current_org_id())
                WITH CHECK (organization_id = current_org_id());
        """)


def disable_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    cursor = schema_editor.connection.cursor()

    all_tables = RLS_TABLES + ORG_TABLES
    for table in all_tables:
        cursor.execute(f"DROP POLICY IF EXISTS org_isolation ON {table};")
        cursor.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    cursor.execute("DROP FUNCTION IF EXISTS current_org_id();")


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0001_initial"),
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]
