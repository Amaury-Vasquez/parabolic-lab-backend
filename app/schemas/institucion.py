from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InstitucionRead(BaseModel):
    idinstitucion: UUID
    clavect: str | None = None
    nombre: str
    fecharegistro: datetime | None = None
    fechamodificacion: datetime | None = None
    activa: bool | None = None
    direccion: str | None = None
    colonia: str | None = None
    municipio: str | None = None
    estado: str | None = None
    codigopostal: str | None = None
    email: str
    telefono: str

    model_config = {"from_attributes": True}
