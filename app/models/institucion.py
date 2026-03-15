import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Institucion(Base):
    __tablename__ = "institucion"
    __table_args__ = (
        Index("idx_institucion_clavect", "clavect"),
        Index("idx_institucion_activa", "activa"),
    )

    idinstitucion: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    clavect: Mapped[str | None] = mapped_column(String, unique=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    fecharegistro: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    fechamodificacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    activa: Mapped[bool | None] = mapped_column(Boolean, server_default="true")
    direccion: Mapped[str | None] = mapped_column(String)
    colonia: Mapped[str | None] = mapped_column(String)
    municipio: Mapped[str | None] = mapped_column(String)
    estado: Mapped[str | None] = mapped_column(String)
    codigopostal: Mapped[str | None] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, nullable=False)
    telefono: Mapped[str] = mapped_column(String, nullable=False)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="institucion")  # noqa: F821
    salones: Mapped[list["Salon"]] = relationship(back_populates="institucion")  # noqa: F821
