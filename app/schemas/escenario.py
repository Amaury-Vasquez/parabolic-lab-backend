from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EscenarioRead(BaseModel):
    idescenario: UUID
    idsalon: UUID
    nombre: str
    descripcion: str | None = None
    niveldificultad: str
    tipoescenario: str
    objetivosaprendizaje: str | None = None
    instrucciones: str | None = None
    tiempolimite: int | None = None
    intentospermitidos: int | None = None
    configuracionescenario: dict[str, Any] | None = None
    fechacreacion: datetime | None = None
    fechamodificacion: datetime | None = None
    activo: bool | None = None

    model_config = {"from_attributes": True}
