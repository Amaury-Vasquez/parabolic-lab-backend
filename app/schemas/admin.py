from uuid import UUID

from pydantic import BaseModel


class AdminRead(BaseModel):
    idadmin: UUID
    idusuario: UUID

    model_config = {"from_attributes": True}
