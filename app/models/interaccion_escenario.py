import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InteraccionEscenario(Base):
    __tablename__ = "interaccionescenario"
    __table_args__ = (
        CheckConstraint("intentosrealizados >= 0", name="interaccionescenario_intentosrealizados_check"),
        CheckConstraint("puntuacion >= 0", name="interaccionescenario_puntuacion_check"),
        CheckConstraint(
            "fechafin IS NULL OR fechafin >= fechainicio",
            name="chk_tiempo_valido",
        ),
        Index("idx_interaccion_escenario", "idescenario"),
        Index("idx_interaccion_alumno", "idalumno"),
        Index("idx_interaccion_fechainicio", "fechainicio"),
        Index("idx_interaccion_completado", "completado"),
    )

    idinteraccion: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    idescenario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escenario.idescenario", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    idalumno: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alumno.idalumno", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    fechainicio: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechamodificacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechafin: Mapped[datetime | None] = mapped_column(DateTime)
    tiempototal: Mapped[int | None] = mapped_column(Integer)
    intentosrealizados: Mapped[int | None] = mapped_column(Integer, server_default="0")
    puntuacion: Mapped[Decimal | None] = mapped_column(Numeric, server_default="0")
    completado: Mapped[bool | None] = mapped_column(Boolean, server_default="false")
    datosinteraccion: Mapped[dict | None] = mapped_column(JSONB, server_default="'{}'::jsonb")

    escenario: Mapped["Escenario"] = relationship(back_populates="interacciones")  # noqa: F821
    alumno: Mapped["Alumno"] = relationship(back_populates="interacciones")  # noqa: F821
