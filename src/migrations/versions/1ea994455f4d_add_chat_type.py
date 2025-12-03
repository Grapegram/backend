"""add_chat_type

Revision ID: 1ea994455f4d
Revises: 1124821f385e
Create Date: 2025-12-03 00:11:51.520706

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1ea994455f4d'
down_revision: Union[str, Sequence[str], None] = '1124821f385e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('chats', sa.Column('type', sa.String(length=50), nullable=False, server_default='group'))

    # Add index for faster queries on type
    op.create_index(op.f('ix_chats_type'), 'chats', ['type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_chats_type'), table_name='chats')
    op.drop_column('chats', 'type')
