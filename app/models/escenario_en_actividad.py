import uuid

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EscenarioEnActividad(Base):
    __tablename__ = "escenarioenactividad"
    __table_args__ = (
        Index("idx_escenario_actividad_escenario", "idescenario"),
        Index("idx_escenario_actividad_actividad", "idactividad"),
    )

    idescenario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escenario.idescenario", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    idactividad: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("actividadinteractiva.idactividad", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    escenario: Mapped["Escenario"] = relationship(back_populates="actividades")  # noqa: F821
    actividad: Mapped["ActividadInteractiva"] = relationship(back_populates="escenarios")  # noqa: F821
