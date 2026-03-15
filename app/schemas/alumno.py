from uuid import UUID

from pydantic import BaseModel


class AlumnoRead(BaseModel):
    idalumno: UUID
    idusuario: UUID
    matricula: str
    idinstitucion: UUID | None = None

    model_config = {"from_attributes": True}
