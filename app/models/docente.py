import uuid

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Docente(Base):
    __tablename__ = "docente"

    iddocente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    idusuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.idusuario"), unique=True, nullable=False
    )
    gradoacademico: Mapped[str | None] = mapped_column(String)

    usuario: Mapped["Usuario"] = relationship(back_populates="docente")  # noqa: F821
    salones: Mapped[list["Salon"]] = relationship(back_populates="docente")  # noqa: F821
