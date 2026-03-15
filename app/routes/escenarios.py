from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.escenario import Escenario
from app.models.usuario import Usuario
from app.schemas.escenario import EscenarioRead

router = APIRouter(prefix="/escenarios", tags=["Escenarios"])


@router.get("/", response_model=list[EscenarioRead])
async def listar_escenarios(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Escenario))
    return result.scalars().all()


@router.get("/{idescenario}", response_model=EscenarioRead)
async def obtener_escenario(
    idescenario: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Escenario).where(Escenario.idescenario == idescenario))
    escenario = result.scalar_one_or_none()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return escenario
