from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UsuarioRead(BaseModel):
    idusuario: UUID
    authid: str
    email: str
    nombre: str
    idinstitucion: UUID
    apellidopaterno: str
    apellidomaterno: str | None = None
    fecharegistro: datetime | None = None
    fechamodificacion: datetime | None = None
    ultimoacceso: datetime | None = None
    activo: bool | None = None
    tipousuario: str

    model_config = {"from_attributes": True}
