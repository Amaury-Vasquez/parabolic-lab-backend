import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlumnoEnSalon(Base):
    __tablename__ = "alumnoensalon"
    __table_args__ = (
        Index("idx_alumno_salon_alumno", "idalumno"),
        Index("idx_alumno_salon_salon", "idsalon"),
        Index("idx_alumno_salon_activo", "activo"),
    )

    idalumno: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alumno.idalumno", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    idsalon: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salon.idsalon", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    fechainscripcion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    activo: Mapped[bool | None] = mapped_column(Boolean, server_default="true")

    alumno: Mapped["Alumno"] = relationship(back_populates="salones")  # noqa: F821
    salon: Mapped["Salon"] = relationship(back_populates="alumnos")  # noqa: F821
