from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AlumnoEnSalonRead(BaseModel):
    idalumno: UUID
    idsalon: UUID
    fechainscripcion: datetime | None = None
    activo: bool | None = None

    model_config = {"from_attributes": True}


class AlumnoEnSalonJoin(BaseModel):
    codigoacceso: str
