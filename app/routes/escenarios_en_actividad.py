from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.escenario_en_actividad import EscenarioEnActividad
from app.models.usuario import Usuario
from app.schemas.escenario_en_actividad import EscenarioEnActividadRead

router = APIRouter(prefix="/escenarios-en-actividad", tags=["EscenariosEnActividad"])


@router.get("/", response_model=list[EscenarioEnActividadRead])
async def listar_escenarios_en_actividad(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(EscenarioEnActividad))
    return result.scalars().all()


@router.get("/{idescenario}/{idactividad}", response_model=EscenarioEnActividadRead)
async def obtener_escenario_en_actividad(
    idescenario: UUID,
    idactividad: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(EscenarioEnActividad).where(
            EscenarioEnActividad.idescenario == idescenario,
            EscenarioEnActividad.idactividad == idactividad,
        )
    )
    registro = result.scalar_one_or_none()
    if not registro:
        raise HTTPException(status_code=404, detail="Relacion escenario-actividad no encontrada")
    return registro
