from uuid import UUID

from pydantic import BaseModel


class EscenarioEnActividadRead(BaseModel):
    idescenario: UUID
    idactividad: UUID

    model_config = {"from_attributes": True}
