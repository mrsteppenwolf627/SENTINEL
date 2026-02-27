"""Initial schema: incidents, plans, audit

Revision ID: a39f60d0d637
Revises:
Create Date: 2026-02-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a39f60d0d637"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- incidents ---
    op.create_table(
        "incidents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("alert_id", sa.String(36), nullable=False, index=True),
        sa.Column("status", sa.String(), server_default="OPEN", index=True),
        sa.Column("source", sa.String(), nullable=False, index=True),
        sa.Column(
            "severity",
            sa.Enum("INFO", "WARNING", "CRITICAL", "FATAL", name="alertseverity"),
            nullable=False,
        ),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), server_default="{}"),
        sa.Column("enriched_context", postgresql.JSONB(), server_default="{}"),
        sa.Column("rca_hypothesis", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            index=True,
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- remediation_plans ---
    op.create_table(
        "remediation_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "incident_id",
            sa.String(36),
            sa.ForeignKey("incidents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("diagnosis_root_cause", sa.String(), nullable=False),
        sa.Column("diagnosis_confidence", sa.Float(), nullable=False),
        sa.Column(
            "action_type",
            sa.Enum(
                "RESTART_SERVICE",
                "CLEAR_CACHE",
                "SCALE_UP",
                "BLOCK_IP",
                "NOTIFICATION",
                "MANUAL_INTERVENTION",
                name="actiontype",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "risk_level",
            sa.Enum("SAFE", "MODERATE", "CRITICAL", name="risklevel"),
            nullable=False,
        ),
        sa.Column("requires_approval", sa.Boolean(), server_default=sa.false()),
        sa.Column("status", sa.String(), server_default="PENDING", index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            index=True,
        ),
        sa.Column("component", sa.String(), nullable=False, index=True),
        sa.Column("event", sa.String(), nullable=False, index=True),
        sa.Column("details", postgresql.JSONB(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("remediation_plans")
    op.drop_table("incidents")
    op.execute("DROP TYPE IF EXISTS alertseverity")
    op.execute("DROP TYPE IF EXISTS actiontype")
    op.execute("DROP TYPE IF EXISTS risklevel")
