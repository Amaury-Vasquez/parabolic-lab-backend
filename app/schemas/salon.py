from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SalonCreate(BaseModel):
    nombresalon: str = Field(..., min_length=1, max_length=100)


class SalonUpdate(BaseModel):
    nombresalon: str | None = Field(None, min_length=1, max_length=100)
    activo: bool | None = None


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