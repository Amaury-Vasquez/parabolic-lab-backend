from uuid import UUID

from pydantic import BaseModel


class DocenteRead(BaseModel):
    iddocente: UUID
    idusuario: UUID
    gradoacademico: str | None = None

    model_config = {"from_attributes": True}
