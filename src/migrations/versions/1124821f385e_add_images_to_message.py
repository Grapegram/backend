"""add_images_to_message

Revision ID: 1124821f385e
Revises: b23fc8e8c62e
Create Date: 2025-12-02 16:43:39.733039

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1124821f385e'
down_revision: Union[str, Sequence[str], None] = 'b23fc8e8c62e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as nullable first to allow existing rows
    op.add_column('messages', sa.Column('images', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Update existing rows to have empty array
    op.execute("UPDATE messages SET images = '[]'::jsonb WHERE images IS NULL")

    # Now make it not nullable with default
    op.alter_column('messages', 'images', nullable=False, server_default='[]')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('messages', 'images')
