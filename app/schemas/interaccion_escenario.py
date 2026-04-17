from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class InteraccionEscenarioRead(BaseModel):
    idinteraccion: UUID
    idescenario: UUID
    idalumno: UUID
    fechainicio: datetime | None = None
    fechamodificacion: datetime | None = None
    fechafin: datetime | None = None
    tiempototal: int | None = None
    intentosrealizados: int | None = None
    puntuacion: Decimal | None = None
    completado: bool | None = None
    datosinteraccion: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class InteraccionEscenarioCreate(BaseModel):
    idescenario: UUID
    idalumno: UUID


class InteraccionEscenarioUpdate(BaseModel):
    fechafin: datetime | None = None
    tiempototal: int | None = None
    puntuacion: Decimal | None = None
    completado: bool | None = None
    datosinteraccion: dict[str, Any] | None = None
