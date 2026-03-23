"""add nombre to usuario

Revision ID: a3f1b2c4d5e6
Revises: c225392f6037
Create Date: 2026-03-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f1b2c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'c225392f6037'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('usuario', sa.Column('nombre', sa.String(), nullable=False, server_default=''))
    op.alter_column('usuario', 'nombre', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('usuario', 'nombre')
