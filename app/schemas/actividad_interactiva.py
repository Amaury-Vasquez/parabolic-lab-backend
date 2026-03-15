from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ActividadInteractivaRead(BaseModel):
    idactividad: UUID
    idsalon: UUID
    titulo: str
    descripcion: str | None = None
    instrucciones: str | None = None
    duracionminutos: int | None = None
    intentospermitidos: int | None = None
    fechacreacion: datetime | None = None
    fechamodificacion: datetime | None = None
    fechaexpiracion: datetime | None = None
    puntuaciontotal: Decimal | None = None
    tipoactividad: str
    activa: bool | None = None

    model_config = {"from_attributes": True}
