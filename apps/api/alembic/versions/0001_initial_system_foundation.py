"""initial system foundation

Revision ID: 0001_initial_system_foundation
Revises: 
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_system_foundation'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create system_audits foundational table
    op.create_table(
        'system_audits',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_audits_event_type'), 'system_audits', ['event_type'], unique=False)


def downgrade() -> None:
    # Drop system_audits table and index
    op.drop_index(op.f('ix_system_audits_event_type'), table_name='system_audits')
    op.drop_table('system_audits')
