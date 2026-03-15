from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.actividad_interactiva import ActividadInteractiva
from app.models.usuario import Usuario
from app.schemas.actividad_interactiva import ActividadInteractivaRead

router = APIRouter(prefix="/actividades-interactivas", tags=["ActividadesInteractivas"])


@router.get("/", response_model=list[ActividadInteractivaRead])
async def listar_actividades_interactivas(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(ActividadInteractiva))
    return result.scalars().all()


@router.get("/{idactividad}", response_model=ActividadInteractivaRead)
async def obtener_actividad_interactiva(
    idactividad: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(ActividadInteractiva).where(ActividadInteractiva.idactividad == idactividad))
    actividad = result.scalar_one_or_none()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad interactiva no encontrada")
    return actividad
