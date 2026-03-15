from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ActividadAlumnoRead(BaseModel):
    idactividadalumno: UUID
    idactividad: UUID
    idalumno: UUID
    puntuacionobtenida: Decimal | None = None
    fechaactividad: datetime | None = None
    fechamodificacion: datetime | None = None
    completada: bool | None = None

    model_config = {"from_attributes": True}
