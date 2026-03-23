from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SalonRead(BaseModel):
    idsalon: UUID
    iddocente: UUID
    idinstitucion: UUID
    codigoacceso: str
    nombresalon: str
    fechacreacion: datetime | None = None
    fechamodificacion: datetime | None = None
    activo: bool | None = None

    model_config = {"from_attributes": True}


class SalonWithDetails(BaseModel):
    idsalon: UUID
    nombresalon: str
    codigoacceso: str
    activo: bool | None = None
    escenarios: list[str] = []
    num_estudiantes: int = 0
