from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AsignarEscenarioRequest(BaseModel):
    idsalon: UUID


class EscenarioCreate(BaseModel):
    idsalon: UUID
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: str | None = None
    niveldificultad: str = Field(..., pattern="^(principiante|intermedio|avanzado|experto)$")
    tipoescenario: str = Field(
        ...,
        pattern="^(simulacion|caso_estudio|problema|proyecto|laboratorio|juego|debate|investigacion)$",
    )
    objetivosaprendizaje: str | None = None
    instrucciones: str | None = None
    tiempolimite: int | None = Field(None, gt=0)
    intentospermitidos: int | None = Field(None, gt=0)
    configuracionescenario: dict[str, Any] | None = None


class EscenarioUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=200)
    descripcion: str | None = None
    niveldificultad: str | None = Field(None, pattern="^(principiante|intermedio|avanzado|experto)$")
    tipoescenario: str | None = Field(
        None,
        pattern="^(simulacion|caso_estudio|problema|proyecto|laboratorio|juego|debate|investigacion)$",
    )
    objetivosaprendizaje: str | None = None
    instrucciones: str | None = None
    tiempolimite: int | None = Field(None, gt=0)
    intentospermitidos: int | None = Field(None, gt=0)
    configuracionescenario: dict[str, Any] | None = None
    activo: bool | None = None


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
