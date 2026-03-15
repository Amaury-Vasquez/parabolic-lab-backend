import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Salon(Base):
    __tablename__ = "salon"
    __table_args__ = (
        Index("idx_salon_codigo_institucion", "codigoacceso", "idinstitucion", unique=True),
        Index("idx_salon_docente", "iddocente"),
        Index("idx_salon_institucion", "idinstitucion"),
        Index("idx_salon_activo", "activo"),
        Index("idx_salon_codigo", "codigoacceso"),
    )

    idsalon: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    iddocente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("docente.iddocente", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    idinstitucion: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institucion.idinstitucion", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    codigoacceso: Mapped[str] = mapped_column(String, nullable=False)
    nombresalon: Mapped[str] = mapped_column(String, nullable=False)
    fechacreacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechamodificacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    activo: Mapped[bool | None] = mapped_column(Boolean, server_default="true")

    docente: Mapped["Docente"] = relationship(back_populates="salones")  # noqa: F821
    institucion: Mapped["Institucion"] = relationship(back_populates="salones")  # noqa: F821
    alumnos: Mapped[list["AlumnoEnSalon"]] = relationship(back_populates="salon")  # noqa: F821
    escenarios: Mapped[list["Escenario"]] = relationship(back_populates="salon")  # noqa: F821
    actividades: Mapped[list["ActividadInteractiva"]] = relationship(back_populates="salon")  # noqa: F821
