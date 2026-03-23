import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        CheckConstraint(
            "tipousuario IN ('alumno', 'docente', 'admin')",
            name="usuario_tipousuario_check",
        ),
        Index("idx_usuario_authid", "authid"),
        Index("idx_usuario_institucion", "idinstitucion"),
        Index("idx_usuario_tipo", "tipousuario"),
    )

    idusuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    # FK to neon_auth.users_sync.id exists in DB but is not modeled here
    # because that table is auto-managed by Neon Auth in a separate schema
    authid: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    idinstitucion: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institucion.idinstitucion", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    apellidopaterno: Mapped[str] = mapped_column(String, nullable=False)
    apellidomaterno: Mapped[str | None] = mapped_column(String)
    fecharegistro: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechamodificacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    ultimoacceso: Mapped[datetime | None] = mapped_column(DateTime)
    activo: Mapped[bool | None] = mapped_column(Boolean, server_default="true")
    tipousuario: Mapped[str] = mapped_column(String, nullable=False)
    temapreferido: Mapped[str | None] = mapped_column(String, server_default="winter")

    institucion: Mapped["Institucion"] = relationship(back_populates="usuarios")  # noqa: F821
    alumno: Mapped["Alumno | None"] = relationship(back_populates="usuario", uselist=False)  # noqa: F821
    admin: Mapped["Admin | None"] = relationship(back_populates="usuario", uselist=False)  # noqa: F821
    docente: Mapped["Docente | None"] = relationship(back_populates="usuario", uselist=False)  # noqa: F821
