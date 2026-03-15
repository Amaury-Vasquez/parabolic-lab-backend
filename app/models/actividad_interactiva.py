import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActividadInteractiva(Base):
    __tablename__ = "actividadinteractiva"
    __table_args__ = (
        CheckConstraint("duracionminutos > 0", name="actividadinteractiva_duracionminutos_check"),
        CheckConstraint("intentospermitidos > 0", name="actividadinteractiva_intentospermitidos_check"),
        CheckConstraint("puntuaciontotal >= 0", name="actividadinteractiva_puntuaciontotal_check"),
        CheckConstraint(
            "tipoactividad IN ("
            "'cuestionario', 'tarea', 'examen', 'proyecto', "
            "'participacion', 'practica', 'foro', 'juego')",
            name="actividadinteractiva_tipoactividad_check",
        ),
        CheckConstraint(
            "fechaexpiracion IS NULL OR fechaexpiracion > fechacreacion",
            name="chk_fecha_expiracion",
        ),
        Index("idx_actividad_salon", "idsalon"),
        Index("idx_actividad_tipo", "tipoactividad"),
        Index("idx_actividad_activa", "activa"),
        Index("idx_actividad_expiracion", "fechaexpiracion"),
        Index("idx_actividad_fecha_creacion", "fechacreacion"),
    )

    idactividad: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    idsalon: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salon.idsalon", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    instrucciones: Mapped[str | None] = mapped_column(Text)
    duracionminutos: Mapped[int | None] = mapped_column(Integer)
    intentospermitidos: Mapped[int | None] = mapped_column(Integer, server_default="1")
    fechacreacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechamodificacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechaexpiracion: Mapped[datetime | None] = mapped_column(DateTime)
    puntuaciontotal: Mapped[Decimal | None] = mapped_column(Numeric, server_default="0")
    tipoactividad: Mapped[str] = mapped_column(String, nullable=False)
    activa: Mapped[bool | None] = mapped_column(Boolean, server_default="true")

    salon: Mapped["Salon"] = relationship(back_populates="actividades")  # noqa: F821
    alumnos: Mapped[list["ActividadAlumno"]] = relationship(back_populates="actividad")  # noqa: F821
    escenarios: Mapped[list["EscenarioEnActividad"]] = relationship(back_populates="actividad")  # noqa: F821
