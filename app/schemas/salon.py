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
