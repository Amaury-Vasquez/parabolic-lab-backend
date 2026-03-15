from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.interaccion_escenario import InteraccionEscenario
from app.models.usuario import Usuario
from app.schemas.interaccion_escenario import InteraccionEscenarioRead

router = APIRouter(prefix="/interacciones-escenario", tags=["InteraccionesEscenario"])


@router.get("/", response_model=list[InteraccionEscenarioRead])
async def listar_interacciones_escenario(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(InteraccionEscenario))
    return result.scalars().all()


@router.get("/{idinteraccion}", response_model=InteraccionEscenarioRead)
async def obtener_interaccion_escenario(
    idinteraccion: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(InteraccionEscenario).where(InteraccionEscenario.idinteraccion == idinteraccion))
    interaccion = result.scalar_one_or_none()
    if not interaccion:
        raise HTTPException(status_code=404, detail="Interaccion de escenario no encontrada")
    return interaccion
