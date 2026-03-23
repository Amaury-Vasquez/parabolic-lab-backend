import uuid

from sqlalchemy import Computed, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alumno(Base):
    __tablename__ = "alumno"
    __table_args__ = (Index("idx_alumno_matricula_institucion", "matricula", "idinstitucion", unique=True),)

    idalumno: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    idusuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.idusuario"), unique=True, nullable=False
    )
    matricula: Mapped[str] = mapped_column(String, nullable=False)
    idinstitucion: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), Computed("get_institucion_from_usuario(idusuario)")
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="alumno")  # noqa: F821
    salones: Mapped[list["AlumnoEnSalon"]] = relationship(back_populates="alumno")  # noqa: F821
    actividades: Mapped[list["ActividadAlumno"]] = relationship(back_populates="alumno")  # noqa: F821
    interacciones: Mapped[list["InteraccionEscenario"]] = relationship(back_populates="alumno")  # noqa: F821
