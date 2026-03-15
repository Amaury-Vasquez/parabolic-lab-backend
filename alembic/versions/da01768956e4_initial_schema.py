"""initial schema

Revision ID: da01768956e4
Revises: 
Create Date: 2026-03-08 17:38:38.284820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da01768956e4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key("fk_admin_usuario", "admin", "usuario", ["idusuario"], ["idusuario"])
    op.create_foreign_key("fk_alumno_usuario", "alumno", "usuario", ["idusuario"], ["idusuario"])
    op.create_foreign_key("fk_docente_usuario", "docente", "usuario", ["idusuario"], ["idusuario"])
    # FK fk_usuario_auth (authid -> neon_auth.users_sync.id) is managed by Neon Auth, not by Alembic


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_docente_usuario", "docente", type_="foreignkey")
    op.drop_constraint("fk_alumno_usuario", "alumno", type_="foreignkey")
    op.drop_constraint("fk_admin_usuario", "admin", type_="foreignkey")
