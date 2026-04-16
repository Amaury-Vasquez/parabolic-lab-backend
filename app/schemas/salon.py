from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SalonCreate(BaseModel):
    nombresalon: str = Field(..., min_length=1, max_length=100)


class SalonUpdate(BaseModel):
    """Schema para actualizar el nombre de un salón (PATCH endpoint)."""

    nombresalon: str = Field(..., min_length=1, max_length=100)


class SalonUpdateFull(BaseModel):
    """Schema para actualización completa de un salón (PUT endpoint)."""

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


class SalonProgresoAlumno(BaseModel):
    """Estadísticas de progreso de un alumno en un salón."""

    idalumno: UUID
    nombre: str
    apellidopaterno: str
    apellidomaterno: str | None = None
    total_interacciones: int
    promedio_puntuacion: Decimal | None = None
    mejor_puntuacion: Decimal | None = None
    total_intentos: int
    escenarios_completados: int
    tiempo_total_minutos: float

    model_config = {"from_attributes": True}


class EstudianteEnSalon(BaseModel):
    """Información de un estudiante en un salón con progreso."""

    idalumno: UUID
    nombre: str
    apellidopaterno: str
    apellidomaterno: str | None = None
    email: str
    ultimo_acceso: datetime | None = None
    escenarios_completados: int
    total_escenarios: int

    model_config = {"from_attributes": True}


class AgregarEstudianteRequest(BaseModel):
    """Solicitud para agregar un estudiante a un salón."""

    correo: str = Field(..., min_length=5, max_length=100)
