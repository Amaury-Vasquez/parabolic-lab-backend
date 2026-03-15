import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActividadAlumno(Base):
    __tablename__ = "actividadalumno"
    __table_args__ = (
        CheckConstraint("puntuacionobtenida >= 0", name="actividadalumno_puntuacionobtenida_check"),
        Index("idx_actividad_alumno_actividad", "idactividad"),
        Index("idx_actividad_alumno_alumno", "idalumno"),
        Index("idx_actividad_alumno_fecha", "fechaactividad"),
    )

    idactividadalumno: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    idactividad: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("actividadinteractiva.idactividad", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    idalumno: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alumno.idalumno", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    puntuacionobtenida: Mapped[Decimal | None] = mapped_column(Numeric, server_default="0")
    fechaactividad: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechamodificacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    completada: Mapped[bool | None] = mapped_column(Boolean, server_default="false")

    actividad: Mapped["ActividadInteractiva"] = relationship(back_populates="alumnos")  # noqa: F821
    alumno: Mapped["Alumno"] = relationship(back_populates="actividades")  # noqa: F821
