from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DocenteRead(BaseModel):
    iddocente: UUID
    idusuario: UUID
    gradoacademico: str | None = None

    model_config = {"from_attributes": True}


class EstudianteGlobalStats(BaseModel):
    """Información de un estudiante con estadísticas globales de todos sus salones."""

    idalumno: UUID
    idusuario: UUID
    nombre: str
    apellidopaterno: str
    apellidomaterno: str | None = None
    email: str
    matricula: str
    nombresalon: str  # Nombre del salón al que pertenece
    # Estadísticas de progreso
    total_interacciones: int
    promedio_puntuacion: Decimal | None = None
    mejor_puntuacion: Decimal | None = None
    total_intentos: int
    escenarios_completados: int
    tiempo_total_minutos: float
    # Progreso como porcentaje (para ordenamiento y visualización)
    progreso_total: float = 0.0

    model_config = {"from_attributes": True}
